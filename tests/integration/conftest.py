"""Integration-specific fixtures, artifacts, and logging hooks."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from html import escape
from datetime import UTC, datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("playwright.async_api")
from playwright.async_api import async_playwright

from tests.integration.settings import IntegrationSettings, ensure_artifact_dirs, load_settings
from xpath_healer.store.json_repository import JsonMetadataRepository


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value).strip("_")


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=True, default=str))
        fh.write("\n")


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except Exception:
                continue
            if isinstance(raw, dict):
                rows.append(raw)
    return rows


@dataclass
class AsyncRuntime:
    loop: asyncio.AbstractEventLoop

    def run(self, awaitable: Any) -> Any:
        return self.loop.run_until_complete(awaitable)


@pytest.fixture(scope="session")
def integration_settings() -> IntegrationSettings:
    settings = load_settings()
    ensure_artifact_dirs(settings)
    return settings


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: Any) -> None:
    settings = load_settings()
    ensure_artifact_dirs(settings)
    if not getattr(config.option, "xmlpath", None):
        config.option.xmlpath = str(settings.junit_xml_path)
    if hasattr(config.option, "cucumberjson") and not getattr(config.option, "cucumberjson", None):
        config.option.cucumberjson = str(settings.cucumber_json_path)


@pytest.fixture(scope="session")
def integration_logger(integration_settings: IntegrationSettings) -> logging.Logger:
    logger = logging.getLogger("xpath_healer.integration")
    logger.setLevel(logging.INFO)
    log_file = integration_settings.logs_dir / "integration.log"
    for handler in list(logger.handlers):
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
            handler.close()
    if not any(
        isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == log_file
        for handler in logger.handlers
    ):
        handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
    return logger


@pytest.fixture(scope="session", autouse=True)
def healing_flow_logger(integration_settings: IntegrationSettings) -> logging.Logger:
    logger = logging.getLogger("xpath_healer")
    logger.setLevel(logging.INFO)
    log_file = integration_settings.logs_dir / "healing-flow.log"
    for handler in list(logger.handlers):
        if isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == log_file:
            logger.removeHandler(handler)
            handler.close()
    if not any(
        isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == log_file
        for handler in logger.handlers
    ):
        handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        logger.addHandler(handler)
    return logger


@pytest.fixture(scope="session", autouse=True)
def prepare_artifacts(integration_settings: IntegrationSettings) -> None:
    # Keep only current run artifacts for clear reporting.
    for path in (
        integration_settings.step_report_jsonl,
        integration_settings.healing_calls_jsonl,
        integration_settings.cucumber_json_path,
        integration_settings.junit_xml_path,
        integration_settings.html_report_path,
    ):
        if path.exists():
            path.unlink()
    for directory, pattern in (
        (integration_settings.screenshots_dir, "*.png"),
        (integration_settings.videos_dir, "*.webm"),
    ):
        for file in directory.glob(pattern):
            try:
                file.unlink()
            except Exception:
                pass


@pytest.fixture(scope="session")
def metadata_repository(integration_settings: IntegrationSettings) -> JsonMetadataRepository:
    return JsonMetadataRepository(integration_settings.metadata_dir)


@pytest.fixture
def runtime() -> Any:
    loop = asyncio.new_event_loop()
    try:
        yield AsyncRuntime(loop=loop)
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


@pytest.fixture
def page(
    runtime: AsyncRuntime,
    request: Any,
    integration_settings: IntegrationSettings,
    integration_logger: logging.Logger,
) -> Any:
    playwright = runtime.run(async_playwright().start())
    browser_type = getattr(playwright, integration_settings.browser_engine, playwright.chromium)

    launch_kwargs: dict[str, Any] = {"headless": integration_settings.headless}
    if integration_settings.browser_channel:
        launch_kwargs["channel"] = integration_settings.browser_channel

    try:
        browser = runtime.run(browser_type.launch(**launch_kwargs))
    except Exception as exc:
        runtime.run(playwright.stop())
        pytest.skip(f"Playwright browser unavailable: {exc}")

    context_kwargs: dict[str, Any] = {}
    if integration_settings.video_each_test:
        context_kwargs["record_video_dir"] = str(integration_settings.videos_dir)
        context_kwargs["record_video_size"] = {
            "width": integration_settings.video_width,
            "height": integration_settings.video_height,
        }
    context = runtime.run(browser.new_context(**context_kwargs))
    p = runtime.run(context.new_page())
    p.set_default_timeout(20_000)
    integration_logger.info(
        "browser_started engine=%s channel=%s headless=%s",
        integration_settings.browser_engine,
        integration_settings.browser_channel or "",
        integration_settings.headless,
    )
    try:
        yield p
    finally:
        test_name = _slug(request.node.name)
        video_path: str | None = None
        # Always capture final screenshot for every test.
        if integration_settings.screenshot_each_test:
            final_path = integration_settings.screenshots_dir / f"{test_name}__final.png"
            try:
                runtime.run(p.screenshot(path=str(final_path), full_page=True))
                integration_logger.info("screenshot_saved test=%s path=%s", test_name, final_path)
            except Exception as exc:
                integration_logger.error("screenshot_failed test=%s error=%s", test_name, exc)

        rep_call = getattr(request.node, "rep_call", None)
        if rep_call and rep_call.failed and integration_settings.screenshot_on_failure:
            fail_path = integration_settings.screenshots_dir / f"{test_name}__failed.png"
            try:
                runtime.run(p.screenshot(path=str(fail_path), full_page=True))
                integration_logger.info("failure_screenshot_saved test=%s path=%s", test_name, fail_path)
            except Exception as exc:
                integration_logger.error("failure_screenshot_failed test=%s error=%s", test_name, exc)

        runtime.run(context.close())
        if integration_settings.video_each_test and getattr(p, "video", None):
            try:
                video_path = runtime.run(p.video.path())
            except Exception:
                pass
        if video_path:
            named_video = integration_settings.videos_dir / f"{test_name}.webm"
            try:
                if named_video.exists():
                    named_video.unlink()
                Path(video_path).replace(named_video)
                integration_logger.info("video_saved test=%s path=%s", test_name, named_video)
            except Exception as exc:
                integration_logger.error("video_rename_failed test=%s source=%s error=%s", test_name, video_path, exc)
        runtime.run(browser.close())
        runtime.run(playwright.stop())


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: Any, call: Any) -> Any:
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        item.rep_call = report


def pytest_bdd_before_scenario(request: Any, feature: Any, scenario: Any) -> None:
    request.node._bdd_step_index = 0


def pytest_bdd_after_step(request: Any, feature: Any, scenario: Any, step: Any, step_func: Any, step_func_args: dict[str, Any]) -> None:
    settings: IntegrationSettings = request.getfixturevalue("integration_settings")
    logger: logging.Logger = request.getfixturevalue("integration_logger")
    runtime: AsyncRuntime = request.getfixturevalue("runtime")
    page = request.getfixturevalue("page")

    request.node._bdd_step_index = int(getattr(request.node, "_bdd_step_index", 0)) + 1
    step_idx = request.node._bdd_step_index
    test_name = _slug(request.node.name)
    step_name = _slug(getattr(step, "name", "step"))
    step_keyword = getattr(step, "keyword", "")
    screenshot_path = None
    if settings.screenshot_each_step:
        screenshot_path = settings.screenshots_dir / f"{test_name}__step{step_idx:02d}__{step_name}.png"
        try:
            runtime.run(page.screenshot(path=str(screenshot_path), full_page=True))
            logger.info(
                "step_screenshot_saved test=%s step=%s keyword=%s path=%s",
                test_name,
                step_name,
                step_keyword.strip(),
                screenshot_path,
            )
        except Exception as exc:
            logger.error("step_screenshot_failed test=%s step=%s error=%s", test_name, step_name, exc)
            screenshot_path = None

    _append_jsonl(
        settings.step_report_jsonl,
        {
            "timestamp": datetime.now(UTC).isoformat(),
            "test": request.node.name,
            "scenario": getattr(scenario, "name", request.node.name),
            "step_index": step_idx,
            "step_keyword": step_keyword.strip(),
            "step_name": getattr(step, "name", ""),
            "status": "passed",
            "screenshot": str(screenshot_path) if screenshot_path else None,
        },
    )


def pytest_bdd_step_error(
    request: Any,
    feature: Any,
    scenario: Any,
    step: Any,
    step_func: Any,
    step_func_args: dict[str, Any],
    exception: Exception,
) -> None:
    settings: IntegrationSettings = request.getfixturevalue("integration_settings")
    logger: logging.Logger = request.getfixturevalue("integration_logger")
    runtime: AsyncRuntime = request.getfixturevalue("runtime")
    page = request.getfixturevalue("page")

    request.node._bdd_step_index = int(getattr(request.node, "_bdd_step_index", 0)) + 1
    step_idx = request.node._bdd_step_index
    test_name = _slug(request.node.name)
    step_name = _slug(getattr(step, "name", "step"))
    step_keyword = getattr(step, "keyword", "")
    screenshot_path = settings.screenshots_dir / f"{test_name}__step{step_idx:02d}__{step_name}__error.png"
    try:
        runtime.run(page.screenshot(path=str(screenshot_path), full_page=True))
        logger.error(
            "step_error_screenshot_saved test=%s step=%s keyword=%s path=%s error=%s",
            test_name,
            step_name,
            step_keyword.strip(),
            screenshot_path,
            exception,
        )
    except Exception as exc:
        logger.error("step_error_screenshot_failed test=%s step=%s error=%s", test_name, step_name, exc)
        screenshot_path = None

    _append_jsonl(
        settings.step_report_jsonl,
        {
            "timestamp": datetime.now(UTC).isoformat(),
            "test": request.node.name,
            "scenario": getattr(scenario, "name", request.node.name),
            "step_index": step_idx,
            "step_keyword": step_keyword.strip(),
            "step_name": getattr(step, "name", ""),
            "status": "failed",
            "error": str(exception),
            "screenshot": str(screenshot_path) if screenshot_path else None,
        },
    )


def pytest_sessionfinish(session: Any, exitstatus: int) -> None:
    settings = load_settings()
    ensure_artifact_dirs(settings)
    steps = _load_jsonl(settings.step_report_jsonl)
    heals = _load_jsonl(settings.healing_calls_jsonl)

    pass_count = len([s for s in steps if s.get("status") == "passed"])
    fail_count = len([s for s in steps if s.get("status") == "failed"])
    summary = (
        f"<p>Step events: passed={pass_count}, failed={fail_count}. "
        f"Session exitstatus={exitstatus}</p>"
    )

    step_rows = []
    for row in steps:
        screenshot = row.get("screenshot")
        screenshot_cell = ""
        if screenshot:
            spath = Path(str(screenshot))
            try:
                if spath.parts and spath.parts[0] == "artifacts":
                    rel = Path("..") / spath.relative_to("artifacts")
                else:
                    rel = spath
            except Exception:
                rel = spath
            screenshot_cell = f'<a href="{escape(str(rel).replace("\\", "/"))}">view</a>'
        step_rows.append(
            "<tr>"
            f"<td>{escape(str(row.get('test', '')))}</td>"
            f"<td>{escape(str(row.get('scenario', '')))}</td>"
            f"<td>{escape(str(row.get('step_index', '')))}</td>"
            f"<td>{escape(str(row.get('step_keyword', '')))}</td>"
            f"<td>{escape(str(row.get('step_name', '')))}</td>"
            f"<td>{escape(str(row.get('status', '')))}</td>"
            f"<td>{screenshot_cell}</td>"
            "</tr>"
        )

    heal_rows = []
    for row in heals:
        selected_kind = row.get("selected_locator_kind", row.get("healed_locator_kind", ""))
        selected_value = row.get("selected_locator_value", row.get("healed_locator_value", ""))
        selected_locator = f"{selected_kind}:{selected_value}" if selected_kind or selected_value else ""
        healed_xpath = row.get("healed_xpath", row.get("robust_xpath", row.get("live_xpath", row.get("healed_locator_value", ""))))
        healed_css = row.get("healed_css", row.get("robust_css", row.get("live_css", "")))
        heal_rows.append(
            "<tr>"
            f"<td>{escape(str(row.get('page_name', '')))}</td>"
            f"<td>{escape(str(row.get('element_name', '')))}</td>"
            f"<td>{escape(str(row.get('status', '')))}</td>"
            f"<td>{escape(str(row.get('strategy_id', '')))}</td>"
            f"<td><code>{escape(str(selected_locator))}</code></td>"
            f"<td><code>{escape(str(row.get('fallback_xpath', '')))}</code></td>"
            f"<td><code>{escape(str(healed_xpath))}</code></td>"
            f"<td>{escape(str(row.get('healed_xpath_source', '')))}</td>"
            f"<td><code>{escape(str(healed_css))}</code></td>"
            f"<td>{escape(str(row.get('healed_css_source', '')))}</td>"
            f"<td>{escape(str(row.get('uniqueness_score', '')))}</td>"
            f"<td>{escape(str(row.get('stability_score', '')))}</td>"
            f"<td>{escape(str(row.get('similarity_score', '')))}</td>"
            f"<td>{escape(str(row.get('overall_score', '')))}</td>"
            "</tr>"
        )

    video_links = []
    for video in sorted(settings.videos_dir.glob("*.webm")):
        rel = Path("..") / Path("videos") / video.name
        video_links.append(f'<li><a href="{escape(str(rel).replace("\\", "/"))}">{escape(video.name)}</a></li>')

    metadata_links = []
    if settings.metadata_dir.exists():
        for meta in sorted(settings.metadata_dir.rglob("*.json")):
            rel = Path("..") / meta.relative_to(settings.artifacts_root)
            metadata_links.append(f'<li><a href="{escape(str(rel).replace("\\", "/"))}">{escape(meta.name)}</a></li>')

    report_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>XPath Healer Integration Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 16px; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 18px; }}
    th, td {{ border: 1px solid #ccc; padding: 6px; vertical-align: top; font-size: 12px; }}
    th {{ background: #f3f3f3; text-align: left; }}
    code {{ white-space: pre-wrap; word-break: break-word; }}
  </style>
</head>
<body>
  <h1>XPath Healer Integration Report</h1>
  {summary}
  <p>
    <a href="integration-junit.xml">JUnit XML</a> |
    <a href="cucumber.json">Cucumber JSON</a> |
    <a href="steps.jsonl">Step JSONL</a> |
    <a href="healing-calls.jsonl">Healing Calls JSONL</a>
  </p>
  <h2>Step Details</h2>
  <table>
    <thead>
      <tr><th>Test</th><th>Scenario</th><th>#</th><th>Keyword</th><th>Step</th><th>Status</th><th>Screenshot</th></tr>
    </thead>
    <tbody>
      {''.join(step_rows)}
    </tbody>
  </table>
  <h2>Healing Calls</h2>
  <table>
    <thead>
      <tr><th>Page</th><th>Element</th><th>Status</th><th>Strategy</th><th>Selected Locator</th><th>Fallback XPath</th><th>Healed XPath</th><th>XPath Source</th><th>Healed CSS</th><th>CSS Source</th><th>Uniqueness</th><th>Stability</th><th>Similarity</th><th>Overall</th></tr>
    </thead>
    <tbody>
      {''.join(heal_rows)}
    </tbody>
  </table>
  <h2>Videos</h2>
  <ul>{''.join(video_links)}</ul>
  <h2>Metadata Files</h2>
  <ul>{''.join(metadata_links)}</ul>
</body>
</html>
"""

    report_path = settings.html_report_path
    report_path.write_text(report_html, encoding="utf-8")
