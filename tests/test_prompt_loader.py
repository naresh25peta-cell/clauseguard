"""
test_prompt_loader.py — tests that prompt files load correctly and parse
into usable FieldSpecs.
"""
from clauseguard.extraction.prompt_loader import load_standard_intro, load_fields

EXPECTED_FIELDS = [
    "NominationRuleDescription",
    "AgreementSection",
    "OptionOwner",
    "AnchorType",
    "Complexity",
    "AnchorDirection",
    "NominationRuleTitle",
]


def test_loads_standard_intro():
    intro = load_standard_intro()
    assert len(intro) > 20
    assert "nomination rule" in intro.lower()


def test_loads_expected_fields():
    fields = load_fields()
    names = [f.name for f in fields]
    assert names == EXPECTED_FIELDS


def test_each_field_has_instruction():
    for field in load_fields():
        assert field.output_type, f"{field.name} missing output_type"
        assert field.instruction, f"{field.name} missing instruction"


def test_allowed_values_parses_closed_lists():
    fields = {f.name: f for f in load_fields()}

    # AgreementSection is categorical
    av = fields["AgreementSection"].allowed_values
    assert av is not None
    assert "Vessel" in av
    assert "ArrivalWindow" in av

    # OptionOwner is categorical
    av = fields["OptionOwner"].allowed_values
    assert av == ["seller", "counterparty", "mutual"]

    # NominationRuleDescription is free text — should return None
    assert fields["NominationRuleDescription"].allowed_values is None
