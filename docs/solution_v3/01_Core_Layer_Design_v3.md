# Core Layer Design v3

## Responsibilities
- Normalize request context.
- Build locator candidates from strategy set.
- Validate candidates against live DOM.
- Score and select winning candidate.

## Key components
- `HealingService`
- `StrategyRegistry` + strategies
- `XPathBuilder`
- `XPathValidator`
- `SimilarityService`
- `SignatureExtractor`
- `PageIndexer`

## Invariants
- No locator is accepted without validation.
- Trace entries are emitted for every stage attempt.
- Result metadata captures quality metrics and selected strategy.

## Failure handling
- Stage-level failures are non-fatal until terminal exhaustion.
- Retry/deep-graph logic is stage-aware.
