# XPath Healer

Deterministic-first locator healing engine with configurable automation adapters, with:
- strategy-based candidate generation
- type-aware validation gates
- signature/similarity scoring
- first-run DOM mining fallback
- in-memory metadata store for standalone operation
- thin FastAPI wrapper

Current adapters:
- `adapters/playwright_python`
- `adapters/selenium_python`

## Quick Start

```bash
python -m pip install -e .[dev,similarity,dom]
python -m pytest -q
```

## Library Usage

```python
from adapters.playwright_python.facade import PlaywrightHealerFacade
from adapters.selenium_python.facade import SeleniumHealerFacade
from xpath_healer.core.models import LocatorSpec

playwright_facade = PlaywrightHealerFacade()
selenium_facade = SeleniumHealerFacade()

# inside async Playwright flow
recovered = await playwright_facade.recover_locator(
    page=page,
    app_id="demo-app",
    page_name="login",
    element_name="username",
    field_type="textbox",
    fallback=LocatorSpec(kind="xpath", value="//input[@id='dynamic-id']"),
    vars={"label": "Username", "data-testid": "username-input"},
)
```

You can also select the adapter through config/env with `XH_ADAPTER=playwright_python` or `XH_ADAPTER=selenium_python` and create the facade via `xpath_healer.create_healer_facade()`.

Integration browser selection is explicit per framework:
- Playwright: `XH_PLAYWRIGHT_BROWSER=chromium|chrome|edge|firefox|webkit`
- Playwright channel override: `XH_PLAYWRIGHT_CHANNEL=chrome|msedge|...`
- Selenium: `XH_SELENIUM_BROWSER=chrome|chromium|edge|firefox`
- Selenium Chromium binary override: `XH_SELENIUM_BINARY=/path/to/chromium`

## API

Run FastAPI wrapper:

```bash
uvicorn service.main:app --reload
```

## Optional DB + RAG Config

Create an `.env` (or set shell env vars) with placeholders:

```bash
OPENAI_API_KEY=<your-openai-key-placeholder>
XH_PG_DSN=postgresql://<user>:<password>@<host>:5432/<db>
XH_CHROMA_PATH=artifacts/chroma
XH_CHROMA_RAG_COLLECTION=xh_rag_documents
XH_CHROMA_ELEMENTS_COLLECTION=xh_elements
XH_ADAPTER=playwright_python
XH_PLAYWRIGHT_BROWSER=chromium
XH_PLAYWRIGHT_CHANNEL=
XH_SELENIUM_BROWSER=chrome
XH_SELENIUM_BINARY=
XH_PG_POOL_MIN=1
XH_PG_POOL_MAX=10
XH_PG_AUTO_INIT_SCHEMA=true
XH_METADATA_JSON_DIR=artifacts/metadata
XH_RAG_ENABLED=false
XH_RAG_TOP_K=5
XH_OPENAI_MODEL=gpt-4.1
XH_OPENAI_EMBED_MODEL=text-embedding-3-small
XH_STAGE_PROFILE=full
XH_STAGE_FALLBACK_ENABLED=true
XH_STAGE_METADATA_ENABLED=true
XH_STAGE_RULES_ENABLED=true
XH_STAGE_FINGERPRINT_ENABLED=true
XH_STAGE_SIGNATURE_ENABLED=true
XH_STAGE_DOM_MINING_ENABLED=true
XH_STAGE_DEFAULTS_ENABLED=true
XH_STAGE_POSITION_ENABLED=true
XH_STAGE_RAG_ENABLED=true
XH_FINGERPRINT_ENABLED=true
XH_FINGERPRINT_MIN_SCORE=0.75
XH_FINGERPRINT_ACCEPT_SCORE=0.90
XH_FINGERPRINT_CANDIDATE_LIMIT=25
XH_RETRY_ENABLED=true
XH_RETRY_MAX_ATTEMPTS=2
XH_RETRY_DELAY_MS=30
XH_RETRY_REASON_CODES=locator_error,locator_timeout,stale_element,not_visible
```

Notes:
- RAG is off by default.
- Adapter selection defaults to `playwright_python`.
- Selenium validation/recovery retries include `stale_element` and `locator_timeout` transient errors by default.
- Stage profile `XH_STAGE_PROFILE=llm_only` disables all deterministic layers and leaves only RAG/LLM stage enabled.
- If `XH_PG_DSN` is set, facade uses dual metadata mode:
  Postgres primary read/write + JSON fallback/backup under `XH_METADATA_JSON_DIR`.
- Fingerprint matching is on by default and runs before signature/vector/LLM fallback.
- When `XH_RAG_ENABLED=true`, facade auto-wires OpenAI + ChromaDB adapters only if both `OPENAI_API_KEY` and `XH_PG_DSN` are valid.
- Retry is lightweight: it only triggers for configured transient reason codes.

## Failure Diagnostics (2026-03-22)

Root cause analysis is documented in:
- `docs/failure_root_cause_2026_03_22.md`

Current test behavior summary:
- TC4 (`@negative`) fails intentionally by test design (`pytest.fail(...)`) to verify raw broken xpath reporting path.
- Under `XH_STAGE_PROFILE=llm_only` with a fresh/wiped DB, TC2 may fail because LLM candidates do not pass validator grounding (`no_match` / `not_visible`) without deterministic fallback layers.

## Solution Design v3

Master design:
- `docs/solution_v3/00_XPath_Healer_Master_Design_v3.md`

Layer design documents:
- `docs/solution_v3/01_Core_Layer_Design_v3.md`
- `docs/solution_v3/02_DB_Layer_Design_v3.md`
- `docs/solution_v3/03_Service_Layer_Design_v3.md`
- `docs/solution_v3/04_Model_RAG_Layer_Design_v3.md`
- `docs/solution_v3/05_Testing_Automation_Layer_Design_v3.md`
