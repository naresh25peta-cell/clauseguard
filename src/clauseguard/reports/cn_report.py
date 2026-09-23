"""
cn_report.py — generates a PDF compliance report for a CN (Cargo Nomination)
               extraction + scoring run.

Renders a summary of extracted vs. expected field values with LLM scores,
using the same reportlab styling conventions as the rest of ClauseGuard.
"""
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER

styles = getSampleStyleSheet()


def _style(name="Normal", **kwargs):
    base = styles[name]
    return ParagraphStyle(name + "_cn_report_" + str(id(kwargs)), parent=base, **kwargs)


TITLE = _style("Heading1", fontSize=16, spaceAfter=6, alignment=TA_CENTER, textColor=colors.HexColor("#1a1a2e"))
SUB   = _style("Normal",   fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor("#16213e"))
H2    = _style("Heading2", fontSize=11, spaceAfter=4, textColor=colors.HexColor("#16213e"))
BODY  = _style("Normal",   fontSize=9,  leading=13, spaceAfter=4)
SMALL = _style("Normal",   fontSize=8,  leading=11, textColor=colors.grey)

SCORE_COLOURS = {5: "#1a7f37", 4: "#1a7f37", 3: "#9a6700", 2: "#cf222e", 1: "#cf222e"}


def _hr():
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"))


def generate_cn_report(
    pdf_filename: str,
    agreement_guid: str,
    trade_group_id: str,
    extracted: dict,
    scores: list,
    output_path,
):
    """
    Build a PDF compliance report summarising extracted CN fields scored
    against NominationRules, and save it to output_path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
    )
    story = []

    story.append(Paragraph("CN COMPLIANCE REPORT", TITLE))
    story.append(Paragraph(f"Source PDF: {pdf_filename}", SUB))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f"Agreement: {agreement_guid}  |  Trade Group: {trade_group_id}  |  "
        f"Generated: {datetime.now().isoformat(timespec='seconds')}", SMALL))
    story.append(Spacer(1, 0.3 * cm))
    story.append(_hr())
    story.append(Spacer(1, 0.4 * cm))

    total = len(scores)
    avg = round(sum(s["score"] for s in scores) / total, 2) if total else 0
    exact = sum(1 for s in scores if s["score"] == 5)
    mismatches = sum(1 for s in scores if s["score"] <= 2)

    story.append(Paragraph("SUMMARY", H2))
    summary_data = [
        [Paragraph("<b>Total fields scored</b>", BODY), Paragraph(str(total), BODY)],
        [Paragraph("<b>Exact matches</b>", BODY), Paragraph(str(exact), BODY)],
        [Paragraph("<b>Mismatches</b>", BODY), Paragraph(str(mismatches), BODY)],
        [Paragraph("<b>Average score</b>", BODY), Paragraph(f"{avg} / 5", BODY)],
    ]
    summary_table = Table(summary_data, colWidths=[6 * cm, 10 * cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dddddd")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("FIELD-BY-FIELD SCORING", H2))
    header = ["Field", "Extracted", "Expected", "Score", "Reasoning"]
    rows = [[Paragraph(f"<b>{h}</b>", BODY) for h in header]]
    for r in scores:
        score = r["score"]
        colour = SCORE_COLOURS.get(score, "#000000")
        rows.append([
            Paragraph(str(r["field"]), BODY),
            Paragraph(str(r["extracted"] or "—")[:200], BODY),
            Paragraph(str(r["expected"] or "—")[:200], BODY),
            Paragraph(f'<font color="{colour}"><b>{score}</b></font>', BODY),
            Paragraph(str(r["reasoning"] or "")[:300], SMALL),
        ])

    field_table = Table(rows, colWidths=[3.2 * cm, 3.3 * cm, 3.3 * cm, 1.5 * cm, 5.2 * cm], repeatRows=1)
    field_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dddddd")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f9fb")]),
    ]))
    story.append(field_table)
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "This report is generated automatically by ClauseGuard for internal review. "
        "Scores are LLM-generated and should be spot-checked for high-stakes decisions.",
        SMALL))

    doc.build(story)
    print(f"  CN report PDF created: {output_path}")

