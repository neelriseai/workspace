# Failure Root Cause Analysis (2026-03-22)

## Scope
This analysis covers the integration BDD runs requested with three configurations:
1. DB wiped, all layers enabled.
2. DB retained, LLM-only.
3. DB wiped again, LLM-only.

## Observed outcomes
- Run A (full): 3 passed, 1 failed.
- Run B (llm_only, warm DB): 3 passed, 1 failed.
- Run C (llm_only, fresh DB): 2 passed, 2 failed.

## Root causes
1. TC4 failure is intentional by test design.
- `tests/integration/test_demo_qa_healing_bdd.py` explicitly calls `pytest.fail(...)` in `report_and_logs_should_show_xpath_failure_reason`.
- This scenario is tagged `@negative` and is expected to fail to validate reporting/logging of raw broken xpath behavior.

2. TC2 failure in LLM-only with fresh DB is a cold-start + visibility grounding issue.
- In llm_only mode, deterministic layers (fallback/metadata/rules/page-index/defaults/position) are disabled.
- With a wiped DB, historical successful selectors and strong warm context are reduced.
- For `home_checkbox_icon`, LLM proposals were:
  - role checkbox with name Home -> validator `no_match`
  - CSS `[id="tree-node-home"]` -> validator `not_visible`
- Result: no candidate passed validation, so recovery failed.

3. Environmental blocker (resolved during execution).
- Initial run attempts failed because `chromadb` dependency was missing.
- After installing `chromadb`, suite execution proceeded and failures became functional/test-design related only.

## Evidence
- `artifacts/logs/healing-flow.log` and `artifacts/logs/integration.log` show:
  - `rag` stage failures with `reason_codes` `no_match` and `not_visible` for TC2 in fresh DB llm_only run.
  - `rag_hallucination` event and final `recover_end` fail for the same correlation flow.
- Pytest output shows TC4 explicit intentional failure message.

## Practical interpretation
- The system is behaving as designed for TC4 (negative test).
- The additional TC2 failure appears only under strict llm_only + cold DB constraints, indicating expected brittleness when no deterministic safety-net is available.

## Recommended actions
1. For CI success gates, split negative scenario from the positive suite.
2. For llm_only cold-start reliability, keep one deterministic fallback (for example metadata or rules) enabled for custom checkbox controls.
3. Add a dedicated llm_only cold-start regression profile with explicit expected-failure rules for known hard controls.
