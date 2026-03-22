# Testing & Automation Layer Design v3

## Responsibilities
- Validate end-to-end healing behavior across adapters and stage profiles.
- Produce reproducible artifacts (screenshots, logs, JSON reports).

## Coverage model
- Positive flows: text-box, checkbox, webtables.
- Negative flow: raw invalid xpath without healer (`@negative`).

## Execution profiles
1. Full profile baseline.
2. LLM-only warm-state regression.
3. LLM-only cold-start regression.

## Reporting artifacts
- `artifacts/logs/healing-flow.log`
- `artifacts/logs/integration.log`
- `artifacts/reports/cucumber*.json`
- Screenshots/videos per scenario.

## Interpretation rule
- `@negative` scenario is expected to fail and should not be mixed with strict pass-only gates.
