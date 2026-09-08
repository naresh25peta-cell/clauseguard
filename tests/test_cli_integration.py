"""
test_cli_integration.py — end-to-end test of the real CLI commands against
the real generated sample PDFs, with only the LLM call mocked.

This exercises the full pipeline that a live run would (PDF parsing ->
prompt building -> response parsing -> DB comparison/storage -> PDF + JSON
report generation) without needing network access or an API key.
"""
import json
import re
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from clauseguard.cli import cli
from clauseguard.database.schema import create_tables

runner = CliRunner()

CN_PDF = Path("data/pdfs/cn/sample_cn.pdf")
MSA_PDF = Path("data/pdfs/msa/sample_msa.pdf")


def _mock_chat_response(content: str):
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    response = MagicMock()
    response.choices = [choice]
    return response


def _extraction_side_effect(*args, **kwargs):
    """Every extraction call gets a plausible VALUE/QUOTE two-line answer."""
    return _mock_chat_response("VALUE: sample extracted value\nQUOTE: sample supporting text")


def _scoring_side_effect(*args, **kwargs):
    """Every scoring call gets a valid JSON score response."""
    return _mock_chat_response(json.dumps({"score": 4, "reasoning": "Close match."}))


def _risk_side_effect(*args, **kwargs):
    """Every clause-rating call gets a valid JSON risk response."""
    return _mock_chat_response(json.dumps({"rating": "Amber", "reasoning": "Standard clause, minor ambiguity."}))


def setup_module(module):
    if not CN_PDF.exists() or not MSA_PDF.exists():
        import subprocess
        subprocess.run(["python", "scripts/generate_sample_pdfs.py"], check=True)
    create_tables()
    from clauseguard.database.seed import seed
    try:
        seed()
    except Exception:
        pass  # already seeded


@patch("clauseguard.extraction.pdf_extractor.client")
@patch("clauseguard.nomination.scorer.client")
def test_check_cn_end_to_end(mock_scorer_client, mock_extractor_client):
    mock_extractor_client.chat.completions.create.side_effect = _extraction_side_effect
    mock_scorer_client.chat.completions.create.side_effect = _scoring_side_effect

    result = runner.invoke(cli, ["check-cn", str(CN_PDF), "AGR-001", "TG-100"])

    assert result.exit_code == 0, result.output
    assert "CN Compliance Scores" in result.output

    report_pdf = Path("reports") / f"{CN_PDF.stem}_compliance_report.pdf"
    report_json = Path("reports") / f"{CN_PDF.stem}_compliance_report.json"
    assert report_pdf.exists()
    assert report_json.exists()

    data = json.loads(report_json.read_text(encoding="utf-8"))
    assert data["agreement_guid"] == "AGR-001"
    assert data["summary"]["total_fields"] > 0


@patch("clauseguard.msa.risk_scanner.client")
def test_scan_msa_end_to_end(mock_client):
    mock_client.chat.completions.create.side_effect = _risk_side_effect

    result = runner.invoke(cli, ["scan-msa", str(MSA_PDF), "periodic"])

    assert result.exit_code == 0, result.output
    assert "MSA Risk Matrix" in result.output

    report_pdf = Path("reports") / f"{MSA_PDF.stem}_risk_report.pdf"
    report_json = Path("reports") / f"{MSA_PDF.stem}_risk_report.json"
    assert report_pdf.exists()
    assert report_json.exists()

    data = json.loads(report_json.read_text(encoding="utf-8"))
    assert data["use_case"] == "periodic"
    assert data["summary"]["total"] > 0
    assert all(c["rating"] in ("Red", "Amber", "Green") for c in data["clauses"])
