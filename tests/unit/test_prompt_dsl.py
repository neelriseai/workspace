from xpath_healer.core.models import BuildInput, Intent, LocatorSpec
from xpath_healer.rag.prompt_builder import build_prompt_payload
from xpath_healer.rag.prompt_dsl import build_prompt_dsl


def test_prompt_dsl_uses_compact_sections() -> None:
    inp = BuildInput(
        page=None,
        app_id="app",
        page_name="checkout",
        element_name="submit_button",
        field_type="button",
        fallback=LocatorSpec(kind="xpath", value="//button[@id='broken-submit']"),
        vars={"label": "Submit Order", "name": "submit-order"},
        intent=Intent.from_vars({"label": "Submit Order", "text": "Submit Order"}),
    )
    dsl = build_prompt_dsl(
        inp,
        "<html><body><form class='checkout'><button id='submit-order'>Submit Order</button></form></body></html>",
        [{"locator": {"kind": "css", "value": "#submit-order", "options": {}}, "rerank_score": 0.97}],
    )

    assert "E submit_button" in dsl
    assert "PG checkout" in dsl
    assert "FT button" in dsl
    assert "F xpath=//button[@id='broken-submit']" in dsl
    assert "A " in dsl
    assert "C" in dsl
    assert "D " in dsl
    assert "O JSON only:" in dsl
    assert "Schema" not in dsl


def test_prompt_payload_exposes_compact_dom_signature_and_output_schema() -> None:
    inp = BuildInput(
        page=None,
        app_id="app",
        page_name="checkout",
        element_name="submit_button",
        field_type="button",
        fallback=LocatorSpec(kind="xpath", value="//button[@id='broken-submit']"),
        vars={},
        intent=Intent.from_vars({"text": "Submit"}),
    )
    payload = build_prompt_payload(
        inp=inp,
        dom_snippet="<html><body><button>Submit</button><button>Cancel</button></body></html>",
        context_candidates=[],
    )

    assert "dom_signature" in payload
    assert "dom_snippet" not in payload
    assert "intent" not in payload
    assert "vars" not in payload
    output_schema = payload["rules"]["output_schema"]
    assert "confidence" in output_schema
    assert "reason" in output_schema
    assert "needs_more_context" in output_schema
    assert payload["mode"] == "default"
