import pytest

from xpath_healer.core.models import ElementMeta, LocatorSpec
from xpath_healer.store.dual_repository import DualMetadataRepository
from xpath_healer.store.memory_repository import InMemoryMetadataRepository


@pytest.mark.asyncio
async def test_dual_repository_reads_primary_then_fallback() -> None:
    primary = InMemoryMetadataRepository()
    fallback = InMemoryMetadataRepository()
    dual = DualMetadataRepository(primary=primary, fallback=fallback)

    meta = ElementMeta(
        app_id="app",
        page_name="page",
        element_name="email",
        field_type="textbox",
        last_good_locator=LocatorSpec(kind="css", value='[name="email"]'),
    )
    await fallback.upsert(meta)

    found = await dual.find("app", "page", "email")
    assert found is not None
    assert found.element_name == "email"

    # Fallback hit should warm primary for next read.
    warmed = await primary.find("app", "page", "email")
    assert warmed is not None


@pytest.mark.asyncio
async def test_dual_repository_dual_writes_to_both_backends() -> None:
    primary = InMemoryMetadataRepository()
    fallback = InMemoryMetadataRepository()
    dual = DualMetadataRepository(primary=primary, fallback=fallback)

    meta = ElementMeta(
        app_id="app",
        page_name="page",
        element_name="submit",
        field_type="button",
        last_good_locator=LocatorSpec(kind="role", value="button", options={"name": "Submit"}),
    )
    await dual.upsert(meta)

    found_primary = await primary.find("app", "page", "submit")
    found_fallback = await fallback.find("app", "page", "submit")
    assert found_primary is not None
    assert found_fallback is not None
