from xpath_healer.core.models import ElementMeta, ElementSignature, HealingHints, LocatorSpec


def test_locator_spec_roundtrip_and_hash_stability() -> None:
    spec = LocatorSpec(
        kind="css",
        value='[data-testid="submit"]',
        options={"nth": 0, "exact": True},
        scope=LocatorSpec(kind="css", value=".dialog"),
    )
    payload = spec.to_dict()
    restored = LocatorSpec.from_dict(payload)
    assert restored.to_dict() == payload
    assert restored.stable_hash() == spec.stable_hash()


def test_element_meta_roundtrip() -> None:
    meta = ElementMeta(
        app_id="app",
        page_name="login",
        element_name="submit",
        field_type="button",
        last_good_locator=LocatorSpec(kind="role", value="button", options={"name": "Submit"}),
        signature=ElementSignature(tag="button", stable_attrs={"data-testid": "submit"}),
        hints=HealingHints(attr_priority_order=["data-testid", "name"], threshold=0.75),
    )
    payload = meta.to_dict()
    restored = ElementMeta.from_dict(payload)
    assert restored.app_id == "app"
    assert restored.page_name == "login"
    assert restored.last_good_locator is not None
    assert restored.last_good_locator.kind == "role"
    assert restored.signature is not None
    assert restored.signature.stable_attrs["data-testid"] == "submit"

