"""Healing orchestration implementing the deterministic cascade."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from xpath_healer.core.builder import XPathBuilder
from xpath_healer.core.context import StrategyContext
from xpath_healer.core.models import (
    BuildInput,
    CandidateSpec,
    ElementMeta,
    LocatorSpec,
    Recovered,
    StrategyTrace,
    ValidationResult,
)
from xpath_healer.utils.ids import new_correlation_id
from xpath_healer.utils.logging import event
from xpath_healer.utils.timing import timed


class HealingService:
    def __init__(self, builder: XPathBuilder) -> None:
        self.builder = builder

    async def recover_locator(self, ctx: StrategyContext, inp: BuildInput) -> Recovered:
        correlation_id = inp.correlation_id or new_correlation_id()
        inp.correlation_id = correlation_id
        trace: list[StrategyTrace] = []

        hints = ctx.resolve_hints(inp.app_id, inp.page_name, inp.element_name, override=inp.hints)
        if not hints.attr_priority_order:
            hints.attr_priority_order = list(ctx.config.attribute_priority)
        inp.hints = hints

        existing_meta = await ctx.repository.find(inp.app_id, inp.page_name, inp.element_name)
        inp.existing_meta = existing_meta

        await self._log_stage_event(
            ctx,
            correlation_id,
            stage="recover_start",
            status="ok",
            inp=inp,
            details={"field_type": inp.field_type},
        )

        # 0) fallback
        fallback_candidate = [CandidateSpec(strategy_id="fallback", locator=inp.fallback, stage="fallback")]
        success = await self._evaluate_candidates(ctx, inp, fallback_candidate, trace)
        if success:
            candidate, validation = success
            return await self._on_success(ctx, inp, candidate, validation, trace)

        # 1) metadata reuse
        metadata_candidates = self._metadata_candidates(existing_meta, inp.field_type)
        if metadata_candidates:
            success = await self._evaluate_candidates(ctx, inp, metadata_candidates, trace)
            if success:
                candidate, validation = success
                return await self._on_success(ctx, inp, candidate, validation, trace)

        # 2) template / rule strategies
        rule_candidates = await self.builder.build_all_candidates(ctx, inp, allowed_stages={"rules"})
        success = await self._evaluate_candidates(ctx, inp, rule_candidates, trace)
        if success:
            candidate, validation = success
            return await self._on_success(ctx, inp, candidate, validation, trace)

        # 3) signature similarity candidates
        signature_candidates = await self._signature_candidates(ctx, inp, existing_meta)
        success = await self._evaluate_candidates(ctx, inp, signature_candidates, trace)
        if success:
            candidate, validation = success
            return await self._on_success(ctx, inp, candidate, validation, trace)

        # 4) first-run robust DOM mining
        dom_candidates = await self._dom_mining_candidates(ctx, inp)
        success = await self._evaluate_candidates(ctx, inp, dom_candidates, trace)
        if success:
            candidate, validation = success
            return await self._on_success(ctx, inp, candidate, validation, trace)

        # Optional RAG stage
        if ctx.config.rag.enabled and ctx.rag_assist:
            rag_candidates = await self._rag_candidates(ctx, inp)
            success = await self._evaluate_candidates(ctx, inp, rag_candidates, trace)
            if success:
                candidate, validation = success
                return await self._on_success(ctx, inp, candidate, validation, trace)

        # 5) code defaults
        default_candidates = await self.builder.build_all_candidates(ctx, inp, allowed_stages={"defaults"})
        success = await self._evaluate_candidates(ctx, inp, default_candidates, trace)
        if success:
            candidate, validation = success
            return await self._on_success(ctx, inp, candidate, validation, trace)

        # 6) position fallback
        position_candidates = await self.builder.build_all_candidates(ctx, inp, allowed_stages={"position"})
        success = await self._evaluate_candidates(ctx, inp, position_candidates, trace)
        if success:
            candidate, validation = success
            return await self._on_success(ctx, inp, candidate, validation, trace)

        await self._persist_failure(ctx, inp, existing_meta)
        await self._log_stage_event(
            ctx,
            correlation_id,
            stage="recover_end",
            status="fail",
            inp=inp,
            details={"reason": "all_strategies_failed"},
        )
        return Recovered(
            status="failed",
            correlation_id=correlation_id,
            strategy_id=None,
            trace=trace,
            error="All healing stages failed to produce a valid locator.",
        )

    async def _evaluate_candidates(
        self,
        ctx: StrategyContext,
        inp: BuildInput,
        candidates: list[CandidateSpec],
        trace: list[StrategyTrace],
    ) -> tuple[CandidateSpec, ValidationResult] | None:
        for candidate in candidates:
            with timed() as span:
                validation = await ctx.validator.validate_candidate(
                    inp.page,
                    candidate.locator,
                    inp.field_type,
                    inp.intent,
                    strict_single_match=inp.hints.strict_single_match if inp.hints else None,
                )

            status = "ok" if validation.ok else "fail"
            stage_trace = StrategyTrace(
                stage=candidate.stage,
                strategy_id=candidate.strategy_id,
                status=status,
                candidate_count=1,
                selected_locator=candidate.locator,
                score=candidate.score,
                validation=validation,
                duration_ms=span.elapsed_ms,
                details=candidate.details,
            )
            trace.append(stage_trace)
            await self._log_stage_event(
                ctx,
                inp.correlation_id,
                stage=candidate.stage,
                status=status,
                inp=inp,
                score=candidate.score,
                details={
                    "strategy_id": candidate.strategy_id,
                    "locator": candidate.locator.to_dict(),
                    "validation": validation.to_dict(),
                },
            )
            if validation.ok:
                return candidate, validation

        if candidates:
            stage = candidates[0].stage
            trace.append(
                StrategyTrace(
                    stage=stage,
                    strategy_id=f"{stage}_summary",
                    status="fail",
                    candidate_count=len(candidates),
                    details={"reason": "no_valid_candidate"},
                )
            )
        return None

    def _metadata_candidates(self, meta: ElementMeta | None, field_type: str) -> list[CandidateSpec]:
        if meta is None:
            return []
        field_type_norm = (field_type or "").strip().casefold()
        out: list[CandidateSpec] = []
        if meta.last_good_locator:
            if not self._is_weak_metadata_locator(meta.last_good_locator, field_type_norm):
                out.append(
                    CandidateSpec(
                        strategy_id="metadata.last_good",
                        locator=meta.last_good_locator,
                        stage="metadata",
                    )
                )
        if meta.robust_locator:
            if not self._is_weak_metadata_locator(meta.robust_locator, field_type_norm):
                out.append(
                    CandidateSpec(
                        strategy_id="metadata.robust",
                        locator=meta.robust_locator,
                        stage="metadata",
                    )
                )
        for key in ("robust_xpath", "robust_css", "live_xpath", "live_css"):
            locator = meta.locator_variants.get(key)
            if not locator:
                continue
            if self._is_weak_metadata_locator(locator, field_type_norm):
                continue
            out.append(
                CandidateSpec(
                    strategy_id=f"metadata.{key}",
                    locator=locator,
                    stage="metadata",
                )
            )
        return out

    async def _signature_candidates(
        self,
        ctx: StrategyContext,
        inp: BuildInput,
        meta: ElementMeta | None,
    ) -> list[CandidateSpec]:
        if meta is None or meta.signature is None:
            return []

        candidates: list[tuple[CandidateSpec, float]] = []
        attr_priority = inp.hints.attr_priority_order if inp.hints and inp.hints.attr_priority_order else ctx.config.attribute_priority
        target_signature = meta.signature

        primary = ctx.signature_extractor.build_robust_locator(target_signature, attr_priority)
        candidates.append(
            (
                CandidateSpec(
                    strategy_id="signature.primary",
                    locator=primary,
                    stage="signature",
                    score=1.0,
                ),
                1.0,
            )
        )

        neighbors = await ctx.repository.find_candidates_by_page(
            inp.app_id,
            inp.page_name,
            inp.field_type,
            limit=25,
        )
        for neighbor in neighbors:
            if not neighbor.signature:
                continue
            if neighbor.element_name == inp.element_name:
                continue
            sim = ctx.similarity.score(target_signature, neighbor.signature)
            threshold = inp.hints.threshold if inp.hints and inp.hints.threshold is not None else ctx.config.similarity_threshold
            if not ctx.similarity.is_similar(sim, threshold=threshold):
                continue
            locator = ctx.signature_extractor.build_robust_locator(neighbor.signature, attr_priority)
            candidates.append(
                (
                    CandidateSpec(
                        strategy_id=f"signature.neighbor:{neighbor.element_name}",
                        locator=locator,
                        stage="signature",
                        score=sim.score,
                        details={"similarity": sim.breakdown},
                    ),
                    sim.score,
                )
            )

        ordered = sorted(candidates, key=lambda item: item[1], reverse=True)
        return [candidate for candidate, _ in ordered]

    async def _dom_mining_candidates(self, ctx: StrategyContext, inp: BuildInput) -> list[CandidateSpec]:
        html = await ctx.dom_snapshotter.capture(inp.page)
        attr_priority = inp.hints.attr_priority_order if inp.hints and inp.hints.attr_priority_order else ctx.config.attribute_priority
        locators = ctx.dom_miner.mine(html, inp.field_type, inp.vars, attr_priority)
        return [
            CandidateSpec(strategy_id="dom_mining", locator=locator, stage="dom_mining")
            for locator in locators
        ]

    async def _rag_candidates(self, ctx: StrategyContext, inp: BuildInput) -> list[CandidateSpec]:
        if not ctx.rag_assist:
            return []
        html = await ctx.dom_snapshotter.capture(inp.page)
        suggestions = await ctx.rag_assist.suggest(inp, html, top_k=ctx.config.rag.top_k)
        return [
            CandidateSpec(strategy_id="rag_suggest", locator=locator, stage="rag", details={"source": "llm"})
            for locator in suggestions
        ]

    async def _on_success(
        self,
        ctx: StrategyContext,
        inp: BuildInput,
        selected: CandidateSpec,
        validation: ValidationResult,
        trace: list[StrategyTrace],
    ) -> Recovered:
        meta = await self._persist_success(
            ctx,
            inp,
            selected.locator,
            selected.strategy_id,
            validation,
            strategy_score=selected.score,
        )
        await self._log_stage_event(
            ctx,
            inp.correlation_id,
            stage="recover_end",
            status="ok",
            inp=inp,
            score=selected.score,
            details={"strategy_id": selected.strategy_id, "locator": selected.locator.to_dict()},
        )
        return Recovered(
            status="success",
            correlation_id=inp.correlation_id,
            locator_spec=selected.locator,
            playwright_locator=selected.locator.to_playwright_locator(inp.page),
            metadata=meta,
            strategy_id=selected.strategy_id,
            trace=trace,
        )

    async def _persist_success(
        self,
        ctx: StrategyContext,
        inp: BuildInput,
        locator: LocatorSpec,
        strategy_id: str,
        validation: ValidationResult,
        strategy_score: float | None = None,
    ) -> ElementMeta:
        meta = inp.existing_meta or ElementMeta(
            app_id=inp.app_id,
            page_name=inp.page_name,
            element_name=inp.element_name,
            field_type=inp.field_type,
        )
        previous_signature = meta.signature
        meta.last_good_locator = locator
        meta.strategy_id = strategy_id
        meta.last_seen = datetime.now(UTC)
        meta.success_count += 1
        meta.locator_variants["last_good"] = locator

        signature = await ctx.signature_extractor.capture(inp.page, locator)
        if signature:
            meta.signature = signature
            attr_priority = inp.hints.attr_priority_order if inp.hints and inp.hints.attr_priority_order else ctx.config.attribute_priority
            robust_css = ctx.signature_extractor.build_robust_locator(signature, attr_priority)
            robust_xpath = ctx.signature_extractor.build_robust_xpath(signature, attr_priority)
            meta.locator_variants["robust_css"] = robust_css
            meta.locator_variants["robust_xpath"] = robust_xpath
            meta.robust_locator = robust_css

        if inp.hints:
            meta.hints = inp.hints

        live_variants = await self._capture_live_locator_variants(inp.page, locator)
        meta.locator_variants.update(live_variants)
        live_css = meta.locator_variants.get("live_css")
        if live_css and self._is_weak_css(meta.robust_locator):
            meta.robust_locator = live_css

        similarity_score = self._similarity_to_previous(ctx, previous_signature, meta.signature)
        quality_metrics = self._build_quality_metrics(
            locator=locator,
            validation=validation,
            similarity_score=similarity_score,
            strategy_id=strategy_id,
            strategy_score=strategy_score,
            signature=meta.signature,
        )
        prior_history = list(meta.quality_metrics.get("history") or [])
        history_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "overall_score": quality_metrics["overall_score"],
            "strategy_id": strategy_id,
            "uniqueness_score": quality_metrics["uniqueness_score"],
            "stability_score": quality_metrics["stability_score"],
            "similarity_score": quality_metrics["similarity_score"],
        }
        quality_metrics["history"] = (prior_history + [history_entry])[-20:]
        meta.quality_metrics = quality_metrics

        if ctx.config.store.enabled:
            await ctx.repository.upsert(meta)
        return meta

    async def _persist_failure(self, ctx: StrategyContext, inp: BuildInput, meta: ElementMeta | None) -> None:
        if meta is None:
            return
        meta.fail_count += 1
        meta.last_seen = datetime.now(UTC)
        if ctx.config.store.enabled:
            await ctx.repository.upsert(meta)

    async def _log_stage_event(
        self,
        ctx: StrategyContext,
        correlation_id: str,
        stage: str,
        status: str,
        inp: BuildInput,
        score: float | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        event(
            logger=ctx.logger,
            level="info",
            message="healing_stage",
            correlation_id=correlation_id,
            stage=stage,
            status=status,
            page_name=inp.page_name,
            element_name=inp.element_name,
            field_type=inp.field_type,
            score=score,
            details=details or {},
        )
        if ctx.config.store.persist_events:
            await ctx.repository.log_event(
                {
                    "correlation_id": correlation_id,
                    "stage": stage,
                    "status": status,
                    "score": score,
                    "app_id": inp.app_id,
                    "page_name": inp.page_name,
                    "element_name": inp.element_name,
                    "field_type": inp.field_type,
                    "details": details or {},
                }
            )

    async def _capture_live_locator_variants(self, page: Any, locator: LocatorSpec) -> dict[str, LocatorSpec]:
        try:
            pw_locator = locator.to_playwright_locator(page)
            count = await pw_locator.count()
            if count <= 0:
                return {}
            target = pw_locator.nth(0)
            payload = await target.evaluate(
                """el => {
                    function xpathFor(node) {
                      if (!node || node.nodeType !== 1) return null;
                      if (node.id) return `//*[@id="${node.id}"]`;
                      const parts = [];
                      let cur = node;
                      while (cur && cur.nodeType === 1) {
                        let idx = 1;
                        let sib = cur.previousElementSibling;
                        while (sib) {
                          if (sib.tagName === cur.tagName) idx += 1;
                          sib = sib.previousElementSibling;
                        }
                        const tag = (cur.tagName || '').toLowerCase();
                        parts.unshift(`${tag}[${idx}]`);
                        cur = cur.parentElement;
                      }
                      return '/' + parts.join('/');
                    }
                    function cssFor(node) {
                      if (!node || node.nodeType !== 1) return null;
                      if (node.id) return `#${node.id}`;
                      const parts = [];
                      let cur = node;
                      while (cur && cur.nodeType === 1 && parts.length < 8) {
                        let part = (cur.tagName || '').toLowerCase();
                        const cls = (cur.className || '').toString().trim().split(/\\s+/).filter(Boolean).slice(0, 2);
                        if (cls.length) part += '.' + cls.join('.');
                        let nth = 1;
                        let sib = cur.previousElementSibling;
                        while (sib) {
                          if (sib.tagName === cur.tagName) nth += 1;
                          sib = sib.previousElementSibling;
                        }
                        part += `:nth-of-type(${nth})`;
                        parts.unshift(part);
                        cur = cur.parentElement;
                      }
                      return parts.join(' > ');
                    }
                    return { xpath: xpathFor(el), css: cssFor(el) };
                }"""
            )
            out: dict[str, LocatorSpec] = {}
            xpath_value = (payload or {}).get("xpath")
            css_value = (payload or {}).get("css")
            if xpath_value:
                out["live_xpath"] = LocatorSpec(kind="xpath", value=str(xpath_value))
            if css_value:
                out["live_css"] = LocatorSpec(kind="css", value=str(css_value))
            return out
        except Exception:
            return {}

    @staticmethod
    def _is_weak_css(locator: LocatorSpec | None) -> bool:
        if locator is None or locator.kind != "css":
            return True
        value = (locator.value or "").strip().lower()
        return value in {"*", "html", "body", "div", "span", "p", "a"}

    @staticmethod
    def _is_weak_metadata_locator(locator: LocatorSpec, field_type_norm: str) -> bool:
        if field_type_norm not in {"text", "label", "generic"}:
            return False
        if locator.kind == "css":
            return (locator.value or "").strip().lower() in {"*", "html", "body"}
        if locator.kind == "xpath":
            value = (locator.value or "").strip().lower()
            return value in {"//*", "//html", "/html[1]"}
        return False

    def _build_quality_metrics(
        self,
        locator: LocatorSpec,
        validation: ValidationResult,
        similarity_score: float | None,
        strategy_id: str,
        strategy_score: float | None,
        signature: Any,
    ) -> dict[str, Any]:
        uniqueness_score = self._uniqueness_score(validation)
        stability_score = self._stability_score(locator, signature)
        weighted = [
            ("uniqueness", uniqueness_score, 0.4),
            ("stability", stability_score, 0.4),
        ]
        if similarity_score is not None:
            weighted.append(("similarity", similarity_score, 0.2))
        total_weight = sum(weight for _, _, weight in weighted)
        overall = sum(score * weight for _, score, weight in weighted) / total_weight if total_weight else 0.0
        return {
            "uniqueness_score": round(uniqueness_score, 4),
            "stability_score": round(stability_score, 4),
            "similarity_score": round(similarity_score, 4) if similarity_score is not None else None,
            "overall_score": round(overall, 4),
            "matched_count": validation.matched_count,
            "chosen_index": validation.chosen_index,
            "validation_reasons": list(validation.reason_codes),
            "strategy_id": strategy_id,
            "strategy_score": round(strategy_score, 4) if strategy_score is not None else None,
            "locator_kind": locator.kind,
            "locator_value": locator.value,
            "valid_against_hints": validation.ok,
        }

    @staticmethod
    def _uniqueness_score(validation: ValidationResult) -> float:
        matched = max(validation.matched_count, 1)
        return min(1.0, 1.0 / matched)

    def _stability_score(self, locator: LocatorSpec, signature: Any) -> float:
        base_map = {
            "role": 0.90,
            "css": 0.78,
            "xpath": 0.70,
            "pw": 0.74,
            "text": 0.62,
        }
        score = base_map.get(locator.kind, 0.60)
        value = (locator.value or "").strip().lower()
        stable_tokens = ("data-testid", "aria-label", "formcontrolname", "name=", "col-id", "aria-colindex")
        if any(token in value for token in stable_tokens):
            score += 0.10
        if locator.kind == "css":
            if ":nth-of-type(" in value:
                score -= 0.10
            if value in {"*", "html", "body", "div", "span"}:
                score -= 0.35
        if locator.kind == "xpath":
            if value.startswith("/"):
                score -= 0.18
            if "[1]" in value and "@id" not in value and "@data-testid" not in value:
                score -= 0.06
            if "@id=" in value or "@data-testid" in value or "@name=" in value:
                score += 0.08
        if locator.kind == "text" and len(value) < 3:
            score -= 0.10

        stable_attr_count = len(getattr(signature, "stable_attrs", {}) or {})
        if stable_attr_count > 0:
            score += min(0.15, 0.03 * stable_attr_count)

        return min(max(score, 0.0), 1.0)

    @staticmethod
    def _similarity_to_previous(ctx: StrategyContext, previous_signature: Any, current_signature: Any) -> float | None:
        if previous_signature is None and current_signature is None:
            return None
        if previous_signature is None and current_signature is not None:
            return 1.0
        if previous_signature is not None and current_signature is None:
            return None
        try:
            sim = ctx.similarity.score(previous_signature, current_signature)
            return sim.score
        except Exception:
            return None
