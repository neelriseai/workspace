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
pip install -e .[dev,similarity,dom]
pytest -q
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

