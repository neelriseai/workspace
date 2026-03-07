# XPath Healer (Phase A Core)

Deterministic-first locator healing engine for Playwright, with:
- strategy-based candidate generation
- type-aware validation gates
- signature/similarity scoring
- first-run DOM mining fallback
- in-memory metadata store for standalone operation
- thin FastAPI wrapper

## Quick Start

```bash
python -m pip install -e .[dev,similarity,dom]
python -m pytest -q
```

## Library Usage

```python
from xpath_healer.api.facade import XPathHealerFacade
from xpath_healer.core.models import LocatorSpec

facade = XPathHealerFacade()

# inside async Playwright flow
recovered = await facade.recover_locator(
    page=page,
    app_id="demo-app",
    page_name="login",
    element_name="username",
    field_type="textbox",
    fallback=LocatorSpec(kind="xpath", value="//input[@id='dynamic-id']"),
    vars={"label": "Username", "data-testid": "username-input"},
)
```

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
XH_PG_POOL_MIN=1
XH_PG_POOL_MAX=10
XH_PG_AUTO_INIT_SCHEMA=true
XH_METADATA_JSON_DIR=artifacts/metadata
XH_RAG_ENABLED=false
XH_RAG_TOP_K=5
XH_OPENAI_MODEL=gpt-4.1
XH_OPENAI_EMBED_MODEL=text-embedding-3-small
XH_RETRY_ENABLED=true
XH_RETRY_MAX_ATTEMPTS=2
XH_RETRY_DELAY_MS=30
XH_RETRY_REASON_CODES=locator_error,not_visible
```

Notes:
- RAG is off by default.
- If `XH_PG_DSN` is set, facade uses dual metadata mode:
  Postgres primary read/write + JSON fallback/backup under `XH_METADATA_JSON_DIR`.
- When `XH_RAG_ENABLED=true`, facade auto-wires OpenAI + pgvector adapters only if both `OPENAI_API_KEY` and `XH_PG_DSN` are valid.
- Retry is lightweight: it only triggers for configured transient reason codes.
