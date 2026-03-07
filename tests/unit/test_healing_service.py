import pytest

from tests.unit.fakes import FakeElement, FakePage
from xpath_healer.api.facade import XPathHealerFacade
from xpath_healer.core.models import LocatorSpec


@pytest.mark.asyncio
async def test_recover_with_attribute_then_metadata_reuse() -> None:
    page = FakePage()
    username = FakeElement(
        tag="input",
        text="",
        attrs={"type": "text", "name": "username", "data-testid": "username-input"},
    )
    page.add_element(username, selectors=['[data-testid="username-input"]', "input"])

    facade = XPathHealerFacade()
    fallback = LocatorSpec(kind="xpath", value="//input[@id='missing-id']")

    first = await facade.recover_locator(
        page=page,
        app_id="app",
        page_name="login",
        element_name="username",
        field_type="textbox",
        fallback=fallback,
        vars={"data-testid": "username-input", "label": "Username"},
    )
    assert first.status == "success"
    assert first.locator_spec is not None
    assert first.strategy_id in {"attribute", "metadata.last_good", "metadata.robust", "metadata.robust_xpath"}

    second = await facade.recover_locator(
        page=page,
        app_id="app",
        page_name="login",
        element_name="username",
        field_type="textbox",
        fallback=fallback,
        vars={},
    )
    assert second.status == "success"
    assert second.strategy_id in {"metadata.last_good", "metadata.robust", "metadata.robust_xpath"}
