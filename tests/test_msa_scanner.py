"""
test_msa_scanner.py — tests the MSA clause splitter and risk rater in isolation.
"""
import json
from unittest.mock import MagicMock, patch
from clauseguard.msa.risk_scanner import _split_clauses, _rate_clause


def test_split_clauses_detects_clause_headings():
    text = """Clause 1 Definitions
This clause defines key terms.

Clause 2 Payment Terms
Payment shall be made within 30 days.

Clause 3 Termination
Either party may terminate with 30 days notice."""

    clauses = _split_clauses(text)
    assert len(clauses) == 3
    assert any("Clause 1" in c["ref"] for c in clauses)
    assert any("Clause 3" in c["ref"] for c in clauses)


def test_split_clauses_falls_back_to_paragraphs():
    # Text with no clause markers — should fall back to paragraph splitting.
    # Paragraphs must be >50 chars to pass the noise filter in the scanner.
    text = (
        "This is the first section covering general terms and conditions of the agreement.\n\n"
        "This is the second section which sets out payment obligations for both parties in detail.\n\n"
        "This is the third section which outlines the termination rights available to each party."
    )
    clauses = _split_clauses(text)
    assert len(clauses) >= 2


def _mock_rating_response(rating: str, reasoning: str):
    msg = MagicMock()
    msg.content = json.dumps({"rating": rating, "reasoning": reasoning})
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


@patch("clauseguard.msa.risk_scanner.client")
def test_rate_clause_red(mock_client):
    mock_client.chat.completions.create.return_value = _mock_rating_response(
        "Red", "Unlimited liability clause poses significant risk."
    )
    rating, reasoning = _rate_clause("Clause 12 Liability", "The seller accepts unlimited liability...", "periodic")
    assert rating == "Red"
    assert len(reasoning) > 0


@patch("clauseguard.msa.risk_scanner.client")
def test_rate_clause_green(mock_client):
    mock_client.chat.completions.create.return_value = _mock_rating_response(
        "Green", "Standard boilerplate — no issues."
    )
    rating, _ = _rate_clause("Clause 1 Definitions", "Definitions as per ISDA standard.", "cmo_check")
    assert rating == "Green"
