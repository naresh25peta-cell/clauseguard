"""
generate_sample_pdfs.py — creates realistic synthetic CN and MSA PDFs for testing.

Run with:
    poetry run python scripts/generate_sample_pdfs.py

Outputs:
    data/pdfs/cn/sample_cn.pdf
    data/pdfs/msa/sample_msa.pdf
"""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── Output paths ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
CN_PATH  = ROOT / "data" / "pdfs" / "cn"  / "sample_cn.pdf"
MSA_PATH = ROOT / "data" / "pdfs" / "msa" / "sample_msa.pdf"

# ── Shared style helpers ──────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def style(name="Normal", **kwargs):
    base = styles[name]
    return ParagraphStyle(
        name + "_custom_" + str(id(kwargs)),
        parent=base,
        **kwargs
    )

H1    = style("Heading1", fontSize=14, spaceAfter=6, textColor=colors.HexColor("#1a1a2e"))
H2    = style("Heading2", fontSize=11, spaceAfter=4, textColor=colors.HexColor("#16213e"))
BODY  = style("Normal",   fontSize=9,  leading=14, spaceAfter=4)
SMALL = style("Normal",   fontSize=8,  leading=12, textColor=colors.grey)
BOLD  = style("Normal",   fontSize=9,  leading=14, fontName="Helvetica-Bold")
CENTER= style("Normal",   fontSize=9,  alignment=TA_CENTER)
RIGHT = style("Normal",   fontSize=8,  alignment=TA_RIGHT, textColor=colors.grey)

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"))

def sp(h=0.3):
    return Spacer(1, h * cm)

def field_table(rows):
    """Render a list of (label, value) pairs as a two-column table."""
    data = [[Paragraph(f"<b>{k}</b>", BODY), Paragraph(v, BODY)] for k, v in rows]
    t = Table(data, colWidths=[5 * cm, 11 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#dddddd")),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ]))
    return t


# ══════════════════════════════════════════════════════════════════════════════
# CARGO NOMINATION (CN)
# ══════════════════════════════════════════════════════════════════════════════

def build_cn():
    doc = SimpleDocTemplate(
        str(CN_PATH), pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm
    )
    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph("SOLACE ENERGY TRADING LTD", style("Normal", fontSize=16, fontName="Helvetica-Bold", alignment=TA_CENTER, textColor=colors.HexColor("#1a1a2e"))))
    story.append(Paragraph("CARGO NOMINATION NOTICE", style("Normal", fontSize=13, alignment=TA_CENTER, textColor=colors.HexColor("#16213e"))))
    story.append(sp(0.2))
    story.append(Paragraph("STRICTLY CONFIDENTIAL — NOT FOR DISTRIBUTION", style("Normal", fontSize=8, alignment=TA_CENTER, textColor=colors.red)))
    story.append(sp(0.4))
    story.append(hr())
    story.append(sp(0.3))

    # ── Reference block ───────────────────────────────────────────────────────
    story.append(field_table([
        ("Document Ref",      "CN-2024-03847"),
        ("Date of Issue",     "14 March 2024"),
        ("Agreement Ref",     "AGR-001"),
        ("Agreement Name",    "Solace-Harbor-DES-2024"),
        ("Trade Group ID",    "TG-100"),
        ("Trade Name",        "LNG Cargo Q3-2024"),
        ("Counterparty",      "Harbor Gas Partners"),
        ("Contract Type",     "DES (Delivered Ex-Ship)"),
    ]))
    story.append(sp(0.5))

    # ── Parties ───────────────────────────────────────────────────────────────
    story.append(Paragraph("1. PARTIES", H2))
    story.append(Paragraph(
        "This Cargo Nomination is issued by <b>Solace Energy Trading Ltd</b> (\"Seller\"), "
        "a company incorporated in England and Wales (Company No. 09876543), whose registered "
        "office is at 12 Riverside Way, Manchester M1 4WQ, to "
        "<b>Harbor Gas Partners</b> (\"Buyer\"), a company incorporated in Germany "
        "(Registry code 40192837), whose registered office is at 8 Nordkai Strasse, 20457 Hamburg, Germany.",
        BODY))
    story.append(sp(0.4))

    # ── Cargo details ─────────────────────────────────────────────────────────
    story.append(Paragraph("2. CARGO DETAILS", H2))
    story.append(field_table([
        ("Commodity",         "Liquefied Natural Gas (LNG)"),
        ("Quantity",          "50,000 metric tonnes (+/- 5% at Seller's option)"),
        ("Energy Content",    "Approximately 2,750,000 MMBtu"),
        ("Quality",           "As per Schedule 2 of the Master Agreement"),
        ("Load Port",         "Sabine Pass LNG Terminal, Louisiana, USA"),
        ("Discharge Port",    "Paldiski LNG Terminal, Estonia"),
        ("Load Laycan",       "15 April 2024 – 20 April 2024 (00:00–23:59 LT)"),
        ("Discharge Window",  "28 April 2024 – 03 May 2024 (00:00–23:59 LT)"),
        ("Incoterms",         "DES Paldiski LNG Terminal"),
        ("Price",             "As per Pricing Schedule — Platts JKM + 0.25 USD/MMBtu"),
    ]))
    story.append(sp(0.4))

    # ── Vessel nomination ─────────────────────────────────────────────────────
    story.append(Paragraph("3. VESSEL NOMINATION", H2))
    story.append(field_table([
        ("Vessel Name",       "LNG NEPTUNE"),
        ("IMO Number",        "9337753"),
        ("Flag",              "Marshall Islands"),
        ("Gross Tonnage",     "93,000 MT"),
        ("LNG Capacity",      "145,000 m³"),
        ("Owner / Operator",  "GDF Suez / Engie"),
        ("Expected ETA Load", "14 April 2024"),
        ("Agent at Load Port","Sabine Pass Terminal Operations Inc."),
    ]))
    story.append(sp(0.4))

    # ── Nomination rules ──────────────────────────────────────────────────────
    story.append(Paragraph("4. NOMINATION RULES AND OBLIGATIONS", H2))

    story.append(Paragraph("4.1  Delivery Window Narrowing", BOLD))
    story.append(Paragraph(
        "Buyer may narrow the delivery window no later than 14 days prior to the start of the "
        "initial delivery window. Such narrowed window shall be a period of three (3) consecutive "
        "days. Once narrowed, the window shall be deemed final and binding on both parties.",
        BODY))
    story.append(sp(0.2))

    story.append(Paragraph("4.2  Vessel Nomination by Seller", BOLD))
    story.append(Paragraph(
        "Seller shall nominate the vessel no later than 5 days prior to the start of the sales "
        "window. The vessel nomination shall include the vessel name, IMO number, estimated "
        "cargo capacity, and expected date of arrival at the load port. Seller may substitute "
        "the nominated vessel with a vessel of equivalent or greater capacity, provided that "
        "written notice is given to Buyer no later than 48 hours prior to commencement of loading.",
        BODY))
    story.append(sp(0.2))

    story.append(Paragraph("4.3  Quantity Nomination", BOLD))
    story.append(Paragraph(
        "Buyer shall nominate the final cargo quantity no later than 10 days prior to the "
        "commencement of loading. The nominated quantity shall be within the tolerance band "
        "specified in Clause 2 above. Failure to nominate within this period shall entitle "
        "Seller to treat the mid-point of the contractual quantity range as the nominated "
        "quantity.",
        BODY))
    story.append(sp(0.4))

    # ── Payment ───────────────────────────────────────────────────────────────
    story.append(Paragraph("5. PAYMENT TERMS", H2))
    story.append(Paragraph(
        "Payment shall be made by irrevocable Letter of Credit in US Dollars, to be opened "
        "no later than 10 banking days prior to the first day of the delivery window. "
        "The Letter of Credit shall be issued by a first-class international bank acceptable "
        "to Seller and shall remain valid for 45 days beyond the last day of the delivery window.",
        BODY))
    story.append(sp(0.4))

    # ── Special conditions ────────────────────────────────────────────────────
    story.append(Paragraph("6. SPECIAL CONDITIONS", H2))
    story.append(Paragraph(
        "This Cargo Nomination is subject to force majeure provisions as set out in Clause 18 "
        "of the Master Agreement. In the event of any conflict between this Cargo Nomination "
        "and the Master Agreement, the terms of the Master Agreement shall prevail.",
        BODY))
    story.append(sp(0.6))

    # ── Signature block ───────────────────────────────────────────────────────
    story.append(hr())
    story.append(sp(0.3))
    story.append(Paragraph("AUTHORISATION", H2))

    sig_data = [
        [Paragraph("<b>For and on behalf of:</b>", BODY), Paragraph("<b>Acknowledged by:</b>", BODY)],
        [Paragraph("Solace Energy Trading Ltd", BODY),     Paragraph("Harbor Gas Partners", BODY)],
        [Paragraph("Signed: ______________________", SMALL), Paragraph("Signed: ______________________", SMALL)],
        [Paragraph("Name:   ______________________", SMALL), Paragraph("Name:   ______________________", SMALL)],
        [Paragraph("Title:  ______________________", SMALL), Paragraph("Title:  ______________________", SMALL)],
        [Paragraph("Date:   14 March 2024",          SMALL), Paragraph("Date:   ______________________", SMALL)],
    ]
    sig_table = Table(sig_data, colWidths=[8*cm, 8*cm])
    sig_table.setStyle(TableStyle([
        ("VALIGN",   (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(sig_table)
    story.append(sp(0.3))
    story.append(Paragraph("This document is generated for local development and testing purposes only. "
                            "Not a legally binding document.", SMALL))

    doc.build(story)
    print(f"  CN PDF created: {CN_PATH}")


# ══════════════════════════════════════════════════════════════════════════════
# MASTER SALES AGREEMENT (MSA)
# ══════════════════════════════════════════════════════════════════════════════

def build_msa():
    doc = SimpleDocTemplate(
        str(MSA_PATH), pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm
    )
    story = []

    # ── Cover ─────────────────────────────────────────────────────────────────
    story.append(Paragraph("MASTER SALES AGREEMENT", style("Normal", fontSize=18, fontName="Helvetica-Bold", alignment=TA_CENTER, textColor=colors.HexColor("#1a1a2e"))))
    story.append(Paragraph("FOR THE SALE AND PURCHASE OF LIQUEFIED NATURAL GAS", style("Normal", fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor("#16213e"))))
    story.append(sp(0.3))
    story.append(Paragraph("STRICTLY CONFIDENTIAL", style("Normal", fontSize=8, alignment=TA_CENTER, textColor=colors.red)))
    story.append(sp(0.2))
    story.append(Paragraph("Agreement Reference: AGR-002  |  Date: 19 February 2024", CENTER))
    story.append(sp(0.4))
    story.append(hr())
    story.append(sp(0.4))

    # ── Parties ───────────────────────────────────────────────────────────────
    story.append(Paragraph("PARTIES", H1))
    story.append(Paragraph(
        "This Master Sales Agreement (\"Agreement\") is entered into as of 19 February 2024 "
        "between:", BODY))
    story.append(sp(0.2))
    story.append(Paragraph(
        "<b>Solace Energy Trading Ltd</b>, a company incorporated in England and Wales "
        "(Company No. 09876543), with registered office at 12 Riverside Way, "
        "Manchester M1 4WQ, United Kingdom (\"Solace\" or \"Seller\");", BODY))
    story.append(sp(0.2))
    story.append(Paragraph("<b>AND</b>", CENTER))
    story.append(sp(0.2))
    story.append(Paragraph(
        "<b>Harbor Gas Partners</b>, a company incorporated under the laws of Germany "
        "(Registry Code 40192837), with registered office at 8 Nordkai Strasse, 20457 "
        "Hamburg, Germany (\"Buyer\" or \"Counterparty\").", BODY))
    story.append(sp(0.4))
    story.append(hr())
    story.append(sp(0.3))

    # ── Clause 1: Definitions ─────────────────────────────────────────────────
    story.append(Paragraph("Clause 1 — Definitions", H2))
    story.append(Paragraph(
        "In this Agreement, the following terms shall have the meanings set out below:", BODY))
    defs = [
        ("\"Cargo Nomination\"",   "A written notice issued by Seller nominating the vessel, quantity, and delivery window for a specific LNG cargo."),
        ("\"Delivery Window\"",    "The period within which delivery of an LNG cargo shall be completed, as specified in each Cargo Nomination."),
        ("\"Initial Window\"",     "The delivery window as first specified in the Cargo Nomination before any narrowing by the Buyer."),
        ("\"Sales Window\"",       "The period during which the Seller may arrange loading of the cargo at the load port terminal."),
        ("\"Nomination Rule\"",    "Any obligation on either party to provide advance notice of a contractual parameter (vessel, quantity, window) by a specified deadline relative to a defined reference point."),
        ("\"RulesDB\"",           "Seller's internal contract management database system of record."),
        ("\"TradeGroupId\"",       "The unique identifier assigned to a group of related LNG trades under this Agreement."),
        ("\"MMBtu\"",              "Million British Thermal Units, the standard unit for measuring LNG energy content."),
    ]
    for term, defn in defs:
        story.append(Paragraph(f"<b>{term}</b>: {defn}", BODY))
    story.append(sp(0.4))

    # ── Clause 2: Quantity ────────────────────────────────────────────────────
    story.append(Paragraph("Clause 2 — Contract Quantity", H2))
    story.append(Paragraph(
        "2.1  The total contract quantity under this Agreement shall be as specified in each "
        "individual Cargo Nomination, subject to a tolerance of plus or minus five percent "
        "(+/- 5%) at Seller's option.", BODY))
    story.append(Paragraph(
        "2.2  Buyer shall nominate the final cargo quantity no later than 10 days prior to "
        "the commencement of loading. The nominated quantity shall fall within the tolerance "
        "band specified in Clause 2.1. Failure to nominate within this period shall entitle "
        "Seller to treat the mid-point of the contractual quantity range as the nominated "
        "quantity for operational purposes.", BODY))
    story.append(sp(0.4))

    # ── Clause 3: Delivery ────────────────────────────────────────────────────
    story.append(Paragraph("Clause 3 — Delivery and Delivery Window", H2))
    story.append(Paragraph(
        "3.1  Delivery shall be made on a DES basis at the Discharge Port specified in the "
        "relevant Cargo Nomination. Risk and title in the LNG shall pass from Seller to Buyer "
        "at the Delivery Point.", BODY))
    story.append(Paragraph(
        "3.2  Buyer may narrow the delivery window no later than 14 days prior to the start "
        "of the initial delivery window. Such narrowed window shall be a period of three (3) "
        "consecutive days. Once narrowed, the delivery window shall be deemed final and "
        "binding on both parties and may not be further amended without mutual written consent.", BODY))
    story.append(Paragraph(
        "3.3  In the event Buyer fails to narrow the delivery window within the period "
        "specified in Clause 3.2, the original Initial Window shall apply.", BODY))
    story.append(sp(0.4))

    # ── Clause 4: Vessel ──────────────────────────────────────────────────────
    story.append(Paragraph("Clause 4 — Vessel Nomination", H2))
    story.append(Paragraph(
        "4.1  Seller shall nominate the vessel no later than 5 days prior to the start of the "
        "Sales Window. The vessel nomination shall include the vessel name, IMO number, flag "
        "state, estimated cargo capacity in cubic metres, and the expected date and time of "
        "arrival at the load port.", BODY))
    story.append(Paragraph(
        "4.2  Seller may substitute the nominated vessel with a vessel of equivalent or greater "
        "capacity, provided that written notice of such substitution is given to Buyer no later "
        "than 48 hours prior to commencement of loading operations.", BODY))
    story.append(Paragraph(
        "4.3  Any vessel nominated under this Clause shall comply with all applicable "
        "international conventions, port regulations, and terminal requirements at both the "
        "load port and the discharge port.", BODY))
    story.append(sp(0.4))

    # ── Clause 5: Price ───────────────────────────────────────────────────────
    story.append(Paragraph("Clause 5 — Price and Payment", H2))
    story.append(Paragraph(
        "5.1  The price per MMBtu for each cargo shall be determined by reference to the "
        "Platts Japan Korea Marker (JKM) index published for the month of delivery, plus "
        "a fixed premium of USD 0.25 per MMBtu.", BODY))
    story.append(Paragraph(
        "5.2  Payment shall be made by irrevocable Letter of Credit in US Dollars within "
        "five (5) banking days of delivery. The Letter of Credit shall be issued by a "
        "first-class international bank acceptable to Seller.", BODY))
    story.append(Paragraph(
        "5.3  Where payment is not received by the due date, Seller shall be entitled to "
        "charge interest on the overdue amount at a rate of USD SOFR plus three percent "
        "(3%) per annum, calculated on a daily basis from the due date until actual payment.", BODY))
    story.append(sp(0.4))

    # ── Clause 6: Liability ───────────────────────────────────────────────────
    story.append(Paragraph("Clause 6 — Limitation of Liability", H2))
    story.append(Paragraph(
        "6.1  Neither party shall be liable to the other for any indirect, consequential, "
        "special or punitive losses or damages arising under or in connection with this "
        "Agreement, whether based in contract, tort (including negligence), strict liability "
        "or otherwise.", BODY))
    story.append(Paragraph(
        "6.2  The aggregate liability of either party under this Agreement in any contract "
        "year shall not exceed the total value of cargoes delivered in that contract year. "
        "This limitation shall not apply in cases of fraud or wilful misconduct.", BODY))
    story.append(sp(0.4))

    # ── Clause 7: Force Majeure ───────────────────────────────────────────────
    story.append(Paragraph("Clause 7 — Force Majeure", H2))
    story.append(Paragraph(
        "7.1  Neither party shall be in breach of this Agreement or liable for delay in "
        "performing, or failure to perform, any of its obligations under this Agreement if "
        "such delay or failure results from a Force Majeure event. Force Majeure events "
        "include but are not limited to: acts of God, war, terrorism, strikes, government "
        "actions, or failure of third-party infrastructure beyond the affected party's "
        "reasonable control.", BODY))
    story.append(Paragraph(
        "7.2  The affected party shall notify the other party in writing within 48 hours "
        "of the occurrence of the Force Majeure event. Failure to provide such notice shall "
        "preclude the affected party from relying on this Clause.", BODY))
    story.append(sp(0.4))

    # ── Clause 8: Termination ─────────────────────────────────────────────────
    story.append(Paragraph("Clause 8 — Termination", H2))
    story.append(Paragraph(
        "8.1  Either party may terminate this Agreement upon ninety (90) days written notice "
        "to the other party, provided that all obligations in respect of cargoes already "
        "nominated under Clause 4 shall continue to apply notwithstanding such termination.", BODY))
    story.append(Paragraph(
        "8.2  Either party may terminate this Agreement immediately upon written notice if "
        "the other party: (a) commits a material breach of this Agreement and fails to remedy "
        "such breach within 30 days of written notice; (b) becomes insolvent or is subject "
        "to insolvency proceedings; or (c) undergoes a change of control without prior written "
        "consent.", BODY))
    story.append(sp(0.4))

    # ── Clause 9: Governing Law ───────────────────────────────────────────────
    story.append(Paragraph("Clause 9 — Governing Law and Dispute Resolution", H2))
    story.append(Paragraph(
        "9.1  This Agreement shall be governed by and construed in accordance with the laws "
        "of England and Wales, without regard to its conflict of laws provisions.", BODY))
    story.append(Paragraph(
        "9.2  Any dispute arising out of or in connection with this Agreement shall be "
        "referred to and finally resolved by arbitration under the LCIA Rules, with the "
        "seat of arbitration in London, England. The language of the arbitration shall be "
        "English.", BODY))
    story.append(sp(0.6))

    # ── Signatures ────────────────────────────────────────────────────────────
    story.append(hr())
    story.append(sp(0.3))
    story.append(Paragraph("EXECUTION", H2))
    story.append(Paragraph(
        "IN WITNESS WHEREOF the parties have executed this Agreement as of the date first "
        "written above.", BODY))
    story.append(sp(0.3))

    sig_data = [
        [Paragraph("<b>Solace Energy Trading Ltd</b>", BOLD), Paragraph("<b>Harbor Gas Partners</b>", BOLD)],
        [Paragraph("Signed: ______________________", SMALL), Paragraph("Signed: ______________________", SMALL)],
        [Paragraph("Name:   ______________________", SMALL), Paragraph("Name:   ______________________", SMALL)],
        [Paragraph("Title:  ______________________", SMALL), Paragraph("Title:  ______________________", SMALL)],
        [Paragraph("Date:   19 February 2024",       SMALL), Paragraph("Date:   19 February 2024",       SMALL)],
    ]
    sig_table = Table(sig_data, colWidths=[8*cm, 8*cm])
    sig_table.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("TOPPADDING", (0,0), (-1,-1), 5)]))
    story.append(sig_table)
    story.append(sp(0.3))
    story.append(Paragraph("This document is generated for local development and testing purposes only. "
                            "Not a legally binding document.", SMALL))

    doc.build(story)
    print(f"  MSA PDF created: {MSA_PATH}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating sample PDFs...")
    build_cn()
    build_msa()
    print("Done.")
