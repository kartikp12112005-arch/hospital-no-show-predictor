"""
PDF report generation module.

Builds a simple, professional one-page PDF summarizing a single
prediction result, using reportlab (a free, open-source library).
"""

import io
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BRAND_BLUE = colors.HexColor("#1768ac")
RISK_RED = colors.HexColor("#e4572e")
SAFE_GREEN = colors.HexColor("#2fae79")
INK = colors.HexColor("#0b2545")


def generate_prediction_report(form_data: dict, result: dict) -> io.BytesIO:
    """
    Render a one-page PDF report for a single prediction.

    Args:
        form_data: The validated patient/appointment input.
        result: The prediction result dict from utils.predictor.predict_no_show.

    Returns:
        An in-memory BytesIO buffer positioned at 0, ready to send_file().
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], textColor=BRAND_BLUE, fontSize=20, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"], textColor=colors.grey, fontSize=10, spaceAfter=20
    )
    section_style = ParagraphStyle(
        "SectionHeading", parent=styles["Heading2"], textColor=INK, fontSize=13, spaceBefore=14, spaceAfter=8
    )
    body_style = styles["Normal"]

    risk_color = RISK_RED if result["risk_level"] == "High Risk" else SAFE_GREEN

    story = []
    story.append(Paragraph("MediPredict — Appointment Prediction Report", title_style))
    story.append(
        Paragraph(
            f"Generated on {datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M UTC')}", subtitle_style
        )
    )

    # ---- Prediction summary block ----
    summary_data = [
        ["Prediction", result["prediction"]],
        ["Risk Level", result["risk_level"]],
        ["Confidence", f"{result['confidence']}%"],
        ["Probability of Attending", f"{result['probability_attend']}%"],
        ["Probability of No-Show", f"{result['probability_no_show']}%"],
    ]
    summary_table = Table(summary_data, colWidths=[7 * cm, 7 * cm])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f4f8fc")),
                ("TEXTCOLOR", (1, 0), (1, 0), risk_color),
                ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e1eaf2")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(summary_table)

    # ---- Patient/appointment details ----
    story.append(Paragraph("Patient & Appointment Details", section_style))
    details_data = [
        ["Gender", "Male" if form_data["gender"] == "M" else "Female"],
        ["Age", str(form_data["age"])],
        ["Scholarship", "Yes" if form_data["scholarship"] else "No"],
        ["Hypertension", "Yes" if form_data["hypertension"] else "No"],
        ["Diabetes", "Yes" if form_data["diabetes"] else "No"],
        ["Alcoholism", "Yes" if form_data["alcoholism"] else "No"],
        ["Handicap Level", str(form_data["handicap"])],
        ["SMS Reminder Received", "Yes" if form_data["sms_received"] else "No"],
        ["Waiting Days", str(form_data["waiting_days"])],
    ]
    details_table = Table(details_data, colWidths=[7 * cm, 7 * cm])
    details_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e1eaf2")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(details_table)

    # ---- Recommendation ----
    story.append(Paragraph("Recommendation", section_style))
    if result["risk_level"] == "High Risk":
        recommendation = (
            "This patient has a high probability of missing the appointment. Consider sending "
            "an additional SMS or phone reminder 24-48 hours before the visit, calling to confirm "
            "attendance, or scheduling a backup patient in the same slot."
        )
    else:
        recommendation = (
            "This patient is likely to attend the appointment as scheduled. Standard reminder "
            "procedures should be sufficient — no additional intervention needed."
        )
    story.append(Paragraph(recommendation, body_style))

    story.append(Spacer(1, 24))
    story.append(
        Paragraph(
            "Generated by MediPredict — Smart Hospital No-Show Prediction & Management System. "
            "This report is generated by a statistical model and should support, not replace, clinical judgment.",
            ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=colors.grey),
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer
