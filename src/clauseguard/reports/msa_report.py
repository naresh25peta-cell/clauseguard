"""
msa_report.py — generates a PDF risk report for an MSA clause-by-clause scan.

Renders a Red/Amber/Green summary and a clause-by-clause ratings table,
using the same reportlab styling conventions as the rest of ClauseGuard.
"""
from pathlib import Path
from datetime import datetime
from collections import Counter
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
    return ParagraphStyle(name + "_msa_report_" + str(id(kwargs)), parent=base, **kwargs)


TITLE = _style("Heading1", fontSize=16, spaceAfter=6, alignment=TA_CENTER, textColor=colors.HexColor("#1a1a2e"))
SUB   = _style("Normal",   fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor("#16213e"))
H2    = _style("Heading2", fontSize=11, spaceAfter=4, textColor=colors.HexColor("#16213e"))
BODY  = _style("Normal",   fontSize=9,  leading=13, spaceAfter=4)
SMALL = _style("Normal",   fontSize=8,  leading=11, textColor=colors.grey)

RATING_COLOURS = {"Red": "#cf222e", "Amber": "#9a6700", "Green": "#1a7f37"}


def _hr():
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"))


def generate_msa_report(
    pdf_filename: str,
    use_case: str,
    results: list,
    output_path,
):
    """
    Build a PDF risk report summarising Red/Amber/Green clause ratings from
    an MSA scan, and save it to output_path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
    )
    story = []

    story.append(Paragraph("MSA RISK REPORT", TITLE))
    story.append(Paragraph(f"Source PDF: {pdf_filename}", SUB))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f"Use case: {use_case}  |  Generated: {datetime.now().isoformat(timespec='seconds')}", SMALL))
    story.append(Spacer(1, 0.3 * cm))
    story.append(_hr())
    story.append(Spacer(1, 0.4 * cm))

    counts = Counter(r["rating"] for r in results)
    story.append(Paragraph("SUMMARY", H2))
    summary_data = [
        [Paragraph("<b>Total clauses reviewed</b>", BODY), Paragraph(str(len(results)), BODY)],
        [Paragraph('<font color="#cf222e"><b>Red</b></font>', BODY), Paragraph(str(counts.get("Red", 0)), BODY)],
        [Paragraph('<font color="#9a6700"><b>Amber</b></font>', BODY), Paragraph(str(counts.get("Amber", 0)), BODY)],
        [Paragraph('<font color="#1a7f37"><b>Green</b></font>', BODY), Paragraph(str(counts.get("Green", 0)), BODY)],
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

    story.append(Paragraph("CLAUSE-BY-CLAUSE RATINGS", H2))
    header = ["Clause", "Rating", "Reasoning"]
    rows = [[Paragraph(f"<b>{h}</b>", BODY) for h in header]]
    for r in results:
        colour = RATING_COLOURS.get(r["rating"], "#000000")
        rows.append([
            Paragraph(str(r["clause_ref"])[:120], BODY),
            Paragraph(f'<font color="{colour}"><b>{r["rating"]}</b></font>', BODY),
            Paragraph(str(r["reasoning"] or "")[:400], SMALL),
        ])

    clause_table = Table(rows, colWidths=[5 * cm, 2.5 * cm, 8.5 * cm], repeatRows=1)
    clause_table.setStyle(TableStyle([
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
    story.append(clause_table)
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "This report is generated automatically by ClauseGuard for internal review. "
        "Ratings are LLM-generated and should be spot-checked for high-stakes decisions.",
        SMALL))

    doc.build(story)
    print(f"  MSA report PDF created: {output_path}")

