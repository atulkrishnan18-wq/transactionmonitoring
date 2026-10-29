"""
ScoreSentinel — FIU-IND STR PDF Generator
Generates formatted, audit-ready Suspicious Transaction Report PDFs with
diagonal watermark, bordered narrative box, footer, and page numbering.
"""

import os
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)


def _draw_watermark_and_footer(canvas, doc):
    """Draws diagonal DRAFT watermark, footer, and page number on every page."""
    canvas.saveState()
    width, height = A4

    # 1. Diagonal Watermark in light grey
    canvas.saveState()
    canvas.translate(width / 2.0, height / 2.0)
    canvas.rotate(42)
    canvas.setFillColor(colors.Color(0.82, 0.82, 0.82, alpha=0.45))
    canvas.setFont("Helvetica-Bold", 38)
    canvas.drawCentredString(0, 0, "DRAFT \u2014 PENDING REVIEW")
    canvas.restoreState()

    # 2. Footer line & text
    canvas.setStrokeColor(colors.HexColor("#CCCCCC"))
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 16 * mm, width - 18 * mm, 16 * mm)

    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(
        18 * mm,
        11 * mm,
        "CONFIDENTIAL \u2014 For FIU-IND submission only. Not for distribution.",
    )
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(
        width - 18 * mm,
        11 * mm,
        f"Page {canvas.getPageNumber()}",
    )

    canvas.restoreState()


def generate_str_pdf(str_data, output_path):
    """
    Creates a formatted FIU-IND STR PDF at output_path from str_data dictionary
    and returns the generated file path.
    """
    abs_path = os.path.abspath(output_path)
    parent_dir = os.path.dirname(abs_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    doc = SimpleDocTemplate(
        abs_path,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=22 * mm,
        title=f"FIU-IND STR - {str_data.get('str_reference', 'DRAFT')}",
        author="ScoreSentinel AML Compliance Engine",
    )

    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        "STRHeader",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#112240"),
        spaceAfter=2,
    )
    subheader_style = ParagraphStyle(
        "STRSubHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#B91C1C"),
        spaceAfter=4,
    )
    entity_banner_style = ParagraphStyle(
        "STREntityBanner",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#333333"),
        spaceAfter=8,
    )
    section_title_style = ParagraphStyle(
        "STRSectionTitle",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#FFFFFF"),
        backColor=colors.HexColor("#1E3A5F"),
        borderPadding=(4, 6, 4, 6),
        spaceBefore=10,
        spaceAfter=6,
    )
    field_style = ParagraphStyle(
        "STRField",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#111111"),
        spaceAfter=2,
    )
    narrative_style = ParagraphStyle(
        "STRNarrative",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#111111"),
    )

    part_a = str_data.get("part_a_reporting_entity", {})
    part_b = str_data.get("part_b_transaction_details", {})
    part_c = str_data.get("part_c_suspect_details", {})
    part_d = str_data.get("part_d_grounds_for_suspicion", {})
    part_e = str_data.get("part_e_metadata", {})

    story = []

    # Document Header
    story.append(Paragraph("FIU-IND Suspicious Transaction Report", header_style))
    story.append(Paragraph("PMLA 2002 \u2014 Section 12 Reporting", subheader_style))
    story.append(
        Paragraph(
            f"<b>Reporting Entity:</b> {escape(str(part_a.get('reporting_entity_name', 'N/A')))} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Report Date:</b> {escape(str(part_a.get('report_date', 'N/A')))} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>STR Reference:</b> {escape(str(str_data.get('str_reference', 'N/A')))}",
            entity_banner_style,
        )
    )
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A5F"), spaceAfter=6))

    def add_field_lines(fields_list):
        for label, value in fields_list:
            safe_label = escape(str(label))
            safe_val = escape(str(value if value is not None else "N/A"))
            story.append(Paragraph(f"<b>{safe_label}:</b> {safe_val}", field_style))

    # SECTION A — Reporting Entity Details
    story.append(Paragraph("SECTION A \u2014 Reporting Entity Details", section_title_style))
    add_field_lines([
        ("Report Type", part_a.get("report_type", "STR")),
        ("Reporting Entity Name", part_a.get("reporting_entity_name")),
        ("Reporting Entity Type", part_a.get("reporting_entity_type")),
        ("FIU-IND Registration No", part_a.get("reporting_entity_fiu_reg_no")),
        ("Principal Officer Name", part_a.get("principal_officer_name")),
        ("Principal Officer Designation", part_a.get("principal_officer_designation")),
        ("Reporting Entity Address", part_a.get("reporting_entity_address")),
        ("Report Date", part_a.get("report_date")),
        ("Period of Transaction", part_a.get("period_of_transaction")),
    ])
    story.append(Spacer(1, 4))

    # SECTION B — Suspicious Transaction Details
    story.append(Paragraph("SECTION B \u2014 Suspicious Transaction Details", section_title_style))
    add_field_lines([
        ("Transaction ID", part_b.get("transaction_id")),
        ("Transaction Date", part_b.get("transaction_date")),
        ("Transaction Amount", part_b.get("transaction_amount")),
        ("Transaction Currency", part_b.get("transaction_currency")),
        ("Transaction Type", part_b.get("transaction_type")),
        ("Mode of Transaction", part_b.get("mode_of_transaction")),
        ("Sender Account", part_b.get("sender_account")),
        ("Sender Bank", part_b.get("sender_bank")),
        ("Receiver Account", part_b.get("receiver_account")),
        ("CRS Score", part_b.get("crs_score")),
        ("Rules Fired", part_b.get("rules_fired")),
        ("Risk Band", part_b.get("risk_band")),
    ])
    story.append(Spacer(1, 4))

    # SECTION C — Suspect Details
    story.append(Paragraph("SECTION C \u2014 Suspect Details", section_title_style))
    add_field_lines([
        ("Suspect Name", part_c.get("suspect_name")),
        ("Suspect Account", part_c.get("suspect_account")),
        ("Customer Type", part_c.get("customer_type")),
        ("PEP Status", part_c.get("pep_status")),
        ("Country of Domicile", part_c.get("country_of_domicile")),
        ("Risk Classification", part_c.get("risk_classification")),
    ])
    story.append(Spacer(1, 4))

    # SECTION D — Grounds for Suspicion (Narrative in a bordered box)
    narrative_text = escape(str(part_d.get("narrative", "N/A")))
    narrative_box = Table(
        [[Paragraph(f"<b>Grounds for Suspicion:</b><br/>{narrative_text}", narrative_style)]],
        colWidths=[174 * mm],
    )
    narrative_box.setStyle(
        TableStyle([
            ("BOX", (0, 0), (-1, -1), 1.2, colors.HexColor("#1E3A5F")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ])
    )
    sec_d_elements = [
        Paragraph("SECTION D \u2014 Grounds for Suspicion (Narrative)", section_title_style),
        Paragraph(f"<b>Alert Type:</b> {escape(str(part_d.get('alert_type', 'N/A')))}", field_style),
        Paragraph(f"<b>Disposition:</b> {escape(str(part_d.get('disposition', 'N/A')))}", field_style),
        Spacer(1, 4),
        narrative_box,
        Spacer(1, 6),
    ]
    story.append(KeepTogether(sec_d_elements))

    # SECTION E — STR Metadata
    story.append(Paragraph("SECTION E \u2014 STR Metadata", section_title_style))
    add_field_lines([
        ("STR Reference", part_e.get("str_reference")),
        ("Alert ID", part_e.get("alert_id")),
        ("Generated At", part_e.get("generated_at")),
        ("Generated By", part_e.get("generated_by")),
        ("Three-Point Standard Met", part_e.get("three_point_met")),
        ("Point 1 Identifier", f"{part_e.get('point_1_identifier')} (Source: {part_e.get('point_1_source', 'N/A')})"),
        ("Point 2 Identifier", f"{part_e.get('point_2_identifier')} (Source: {part_e.get('point_2_source', 'N/A')})"),
        ("Point 3 Identifier", f"{part_e.get('point_3_identifier')} (Source: {part_e.get('point_3_source', 'N/A')})"),
        ("Status", part_e.get("status")),
    ])

    doc.build(
        story,
        onFirstPage=_draw_watermark_and_footer,
        onLaterPages=_draw_watermark_and_footer,
    )

    return abs_path
