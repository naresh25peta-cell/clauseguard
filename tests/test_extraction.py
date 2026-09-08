"""
test_extraction.py — tests the field-by-field prompt building and
extraction loop using a mock LLM.
"""
from pathlib import Path
from unittest.mock import MagicMock
from clauseguard.extraction.pdf_extractor import build_field_prompt
from clauseguard.extraction.prompt_loader import load_standard_intro, load_fields, FieldSpec

FIXTURE_CLAUSE = (
    Path(__file__).parent / "fixtures" / "synthetic_clause.txt"
).read_text(encoding="utf-8")


def _mock_llm(responses: dict[str, str]):
    """Build a mock LLM client that returns canned responses by field name."""
    mock = MagicMock()
    def complete(prompt: str) -> str:
        for field_name, value in responses.items():
            if f"Field to extract: {field_name}" in prompt:
                return value
        return "UNKNOWN"
    mock.complete.side_effect = complete
    return mock


def test_build_field_prompt_includes_all_parts():
    intro = load_standard_intro()
    field = load_fields()[0]  # NominationRuleDescription
    prompt = build_field_prompt(field, intro, FIXTURE_CLAUSE)

    assert intro[:30] in prompt
    assert f"Field to extract: {field.name}" in prompt
    assert field.instruction[:30] in prompt
    assert FIXTURE_CLAUSE[:30] in prompt
    assert "Return your answer in exactly two lines" in prompt


def test_prompt_calls_llm_once_per_field():
    fields = load_fields()
    intro = load_standard_intro()
    llm = MagicMock()
    llm.complete.return_value = "test_value"

    results = {}
    for field in fields:
        prompt = build_field_prompt(field, intro, FIXTURE_CLAUSE)
        results[field.name] = llm.complete(prompt).strip()

    assert llm.complete.call_count == len(fields)
    assert len(results) == len(fields)


def test_extraction_routes_responses_by_field_name():
    fields = load_fields()
    intro = load_standard_intro()

    canned = {
        "NominationRuleDescription": "Buyer may narrow the delivery window...",
        "AgreementSection":          "ArrivalWindow",
        "OptionOwner":               "counterparty",
        "AnchorType":                "InitialWindow",
        "Complexity":                "SimpleAnchor",
        "AnchorDirection":           "Before",
        "NominationRuleTitle":       "Agreement * counterparty shall nom * ArrivalWindow",
    }
    llm = _mock_llm(canned)

    results = {}
    for field in fields:
        prompt = build_field_prompt(field, intro, FIXTURE_CLAUSE)
        results[field.name] = llm.complete(prompt).strip()

    assert results["AgreementSection"] == "ArrivalWindow"
    assert results["OptionOwner"] == "counterparty"
    assert results["AnchorDirection"] == "Before"


def test_extraction_strips_whitespace():
    fields = [load_fields()[2]]  # OptionOwner
    intro = load_standard_intro()
    llm = _mock_llm({"OptionOwner": "  seller  \n"})

    prompt = build_field_prompt(fields[0], intro, FIXTURE_CLAUSE)
    value = llm.complete(prompt).strip()
    assert value == "seller"
