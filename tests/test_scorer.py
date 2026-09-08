"""
test_scorer.py — tests the LLM scorer in isolation by mocking the OpenAI call.
"""
import json
from unittest.mock import MagicMock, patch
from clauseguard.nomination.scorer import score_field


def _mock_response(score: int, reasoning: str):
    msg = MagicMock()
    msg.content = json.dumps({"score": score, "reasoning": reasoning})
    choice = MagicMock()
    choice.message = msg
    response = MagicMock()
    response.choices = [choice]
    return response


@patch("clauseguard.nomination.scorer.client")
def test_score_exact_match(mock_client):
    mock_client.chat.completions.create.return_value = _mock_response(5, "Values match exactly.")
    score, reasoning = score_field("OptionOwner", "seller", "seller")
    assert score == 5
    assert "match" in reasoning.lower()


@patch("clauseguard.nomination.scorer.client")
def test_score_mismatch(mock_client):
    mock_client.chat.completions.create.return_value = _mock_response(1, "Completely different values.")
    score, _ = score_field("AgreementSection", "Vessel", "ArrivalWindow")
    assert score == 1


@patch("clauseguard.nomination.scorer.client")
def test_score_missing_field(mock_client):
    mock_client.chat.completions.create.return_value = _mock_response(1, "Field not found in the document.")
    score, _ = score_field("AnchorType", None, "InitialWindow")
    assert score == 1


@patch("clauseguard.nomination.scorer.client")
def test_score_partial_match(mock_client):
    mock_client.chat.completions.create.return_value = _mock_response(4, "Minor capitalisation difference.")
    score, _ = score_field("OptionOwner", "SELLER", "seller")
    assert score == 4
