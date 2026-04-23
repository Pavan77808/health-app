"""
reports/generator.py
Generates PDF reports for patients using ReportLab
Covers: Registration, Bill, Prescription, Lab Report
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

HOSPITAL_NAME    = "PAVAN HEALTH CARE"
HOSPITAL_ADDRESS = "123 Health Street, Bengaluru, Karnataka - 560001"
HOSPITAL_PHONE   = "+91 9876543210"
HOSPITAL_EMAIL   = "info@pavanhealth.com"

PRIMARY_COLOR   = colors.HexColor("#2563eb")
SECONDARY_COLOR = colors.HexColor("#1e3a5f")
ACCENT_COLOR    = colors.HexColor("#dc2626")
LIGHT_BLUE      = colors.HexColor("#dbeafe")
LIGHT_GRAY      = colors.HexColor("#f3f4f6")
WHITE           = colors.white
BLACK           = colors.black


def get_styles():
    styles = getSampleStyleSheet()
    custom = {
        "hospital_name": ParagraphStyle(
            "hospital_name",
            fontSize=20,
            textColor=PRIMARY_COLOR,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
            spaceAfter=4
        ),
        "hospital_sub": ParagraphStyle(
            "hospital_sub",
            fontSize=9,
            textColor=colors.HexColor("#555555"),
            fontName="Helvetica",
            alignment=TA_CENTER,
            spaceAfter=2
        ),
        "report_title": ParagraphStyle(
            "report_title",
            fontSize=14,
            textColor=WHITE,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
            spaceAfter=6
        ),
        "section_title": ParagraphStyle(
            "section_title",
            fontSize=11,
            textColor=SECONDARY_COLOR,
            fontName="Helvetica-Bold",
            spaceAfter=6,
            spaceBefore=10
        ),
        "normal": ParagraphStyle(
            "normal_text",
            fontSize=9,
            textColor=BLACK,
            fontName="Helvetica",
            spaceAfter=4
        ),
        "label": ParagraphStyle(
            "label",
            fontSize=8,
            textColor=colors.HexColor("#666666"),
            fontName="Helvetica",
        ),
        "value": ParagraphStyle(
            "value",
            fontSize=9,
            textColor=BLACK,
            fontName="Helvetica-Bold",
        ),
        "footer": ParagraphStyle(
            "footer",
            fontSize=8,
            textColor=colors.HexColor("#888888"),
            fontName="Helvetica",
            alignment=TA_CENTER,
        ),
        "amount": ParagraphStyle(
            "amount",
            fontSize=12,
            textColor=PRIMARY_COLOR,
            fontName="Helvetica-Bold",
            alignment=TA_RIGHT,
        ),
    }
    return custom


def build_header(styles, report_type):
    elements = []

    # Hospital name
    elements.append(Paragraph(HOSPITAL_NAME, styles["hospital_name"]))
    elements.append(Paragraph(HOSPITAL_ADDRESS, styles["hospital_sub"]))
    elements.append(Paragraph(
        f"Phone: {HOSPITAL_PHONE}  |  Email: {HOSPITAL_EMAIL}",
        styles["hospital_sub"]
    ))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(
        width="100%", thickness=2,
        color=PRIMARY_COLOR, spaceAfter=6
    ))

    # Report title banner
    title_table = Table(
        [[Paragraph(report_type, styles["report_title"])]],
        colWidths=["100%"]
    )
    title_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY_COLOR),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(title_table)
    elements.append(Spacer(1, 12))

    return elements


def build_footer(styles):
    elements = []
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(
        width="100%", thickness=1,
        color=colors.HexColor("#dddddd"),
        spaceAfter=6
    ))
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    elements.append(Paragraph(
        f"Generated on: {now}  |  {HOSPITAL_NAME}  |  This is a computer generated report",
        styles["footer"]
    ))
    return elements


def info_table(data, styles):
    rows = []
    for i in range(0, len(data), 2):
        row = []
        for j in range(2):
            if i + j < len(data):
                label, value = data[i + j]
                cell = [
                    Paragraph(label, styles["label"]),
                    Paragraph(str(value) if value else "-", styles["value"])
                ]
                row.append(cell)
            else:
                row.append("")
        rows.append(row)

    t = Table(rows, colWidths=[2.8 * inch, 2.8 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), LIGHT_GRAY),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("TOPPADDING",  (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0,0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",(0, 0), (-1, -1), 8),
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
    ]))
    return t


# ═══════════════════════════════════════════
# REPORT 1: PATIENT REGISTRATION REPORT
# ═══════════════════════════════════════════

def generate_registration_report(patient_data: dict, doctor_data: dict = None) -> str:
    filename = f"patient_registration_{patient_data.get('id', 'new')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )

    styles   = get_styles()
    elements = []

    # Header
    elements += build_header(styles, "PATIENT REGISTRATION REPORT")

    # Patient ID badge
    pid = str(patient_data.get("id", "N/A"))
    badge = Table(
        [[
            Paragraph("PATIENT ID", styles["label"]),
            Paragraph(f"# {pid}", ParagraphStyle(
                "pid", fontSize=16, textColor=PRIMARY_COLOR,
                fontName="Helvetica-Bold", alignment=TA_RIGHT
            ))
        ]],
        colWidths=["50%", "50%"]
    )
    badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    elements.append(badge)
    elements.append(Spacer(1, 12))

    # Personal Details
    elements.append(Paragraph("Personal Information", styles["section_title"]))
    personal = [
        ("Full Name",        f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}"),
        ("Date of Birth",    patient_data.get("date_of_birth", "-")),
        ("Gender",           patient_data.get("gender", "-").capitalize() if patient_data.get("gender") else "-"),
        ("Blood Group",      patient_data.get("blood_group", "-")),
        ("Phone",            patient_data.get("phone", "-")),
        ("Email",            patient_data.get("email", "-")),
        ("Address",          patient_data.get("address", "-")),
        ("Allergies",        patient_data.get("allergies", "None")),
    ]
    elements.append(info_table(personal, styles))
    elements.append(Spacer(1, 10))

    # Emergency Contact
    elements.append(Paragraph("Emergency Contact", styles["section_title"]))
    emergency = [
        ("Contact Name",  patient_data.get("emergency_contact", "-")),
        ("Contact Phone", patient_data.get("emergency_phone", "-")),
    ]
    elements.append(info_table(emergency, styles))
    elements.append(Spacer(1, 10))

    # Insurance Details
    elements.append(Paragraph("Insurance Details", styles["section_title"]))
    insurance = [
        ("Insurance Provider", patient_data.get("insurance_provider", "-")),
        ("Insurance ID",       patient_data.get("insurance_id", "-")),
    ]
    elements.append(info_table(insurance, styles))
    elements.append(Spacer(1, 10))

    # Doctor Assignment
    if doctor_data:
        elements.append(Paragraph("Assigned Doctor", styles["section_title"]))
        doctor = [
            ("Doctor Name",     f"Dr. {doctor_data.get('first_name', '')} {doctor_data.get('last_name', '')}"),
            ("Specialization",  doctor_data.get("specialization", "-")),
            ("License No",      doctor_data.get("license_number", "-")),
            ("Consultation Fee",f"Rs. {doctor_data.get('consultation_fee', 0)}"),
        ]
        elements.append(info_table(doctor, styles))
        elements.append(Spacer(1, 10))

    # Signature section
    elements.append(Spacer(1, 20))
    sig_table = Table(
        [["Patient Signature", "Doctor Signature", "Authorized Signature"]],
        colWidths=["33%", "33%", "34%"]
    )
    sig_table.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 40),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("TEXTCOLOR",     (0, 0), (-1, -1), colors.HexColor("#666666")),
        ("LINEABOVE",     (0, 0), (-1, -1), 1, colors.HexColor("#aaaaaa")),
    ]))
    elements.append(sig_table)

    elements += build_footer(styles)

    doc.build(elements)
    print(f"Registration report generated: {filepath}")
    return filepath


# ═══════════════════════════════════════════
# REPORT 2: BILL / INVOICE PDF
# ═══════════════════════════════════════════

def generate_bill_report(bill_data: dict, patient_data: dict) -> str:
    filename = f"invoice_{bill_data.get('invoice_number', 'INV')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        rightMargin=1.5 * cm, leftMargin=1.5 * cm,
        topMargin=1.5 * cm,   bottomMargin=1.5 * cm
    )

    styles   = get_styles()
    elements = []

    elements += build_header(styles, "INVOICE / BILL")

    # Invoice number and date
    inv_table = Table(
        [[
            Paragraph(f"Invoice No: <b>{bill_data.get('invoice_number', '-')}</b>", styles["normal"]),
            Paragraph(
                f"Date: {datetime.now().strftime('%d-%m-%Y')}",
                ParagraphStyle("r", fontSize=9, alignment=TA_RIGHT,
                               fontName="Helvetica")
            )
        ]],
        colWidths=["50%", "50%"]
    )
    inv_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    elements.append(inv_table)
    elements.append(Spacer(1, 10))

    # Patient details
    elements.append(Paragraph("Patient Details", styles["section_title"]))
    pat_info = [
        ("Patient Name", f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}"),
        ("Patient ID",   str(patient_data.get("id", "-"))),
        ("Phone",        patient_data.get("phone", "-")),
        ("Blood Group",  patient_data.get("blood_group", "-")),
    ]
    elements.append(info_table(pat_info, styles))
    elements.append(Spacer(1, 10))

    # Charges table
    elements.append(Paragraph("Charges Breakdown", styles["section_title"]))
    charges = [
        ["Description", "Amount (Rs.)"],
        ["Consultation Fee",  f"Rs. {bill_data.get('consultation_fee', 0):.2f}"],
        ["Medicine Charges",  f"Rs. {bill_data.get('medicine_charges', 0):.2f}"],
        ["Lab Charges",       f"Rs. {bill_data.get('lab_charges', 0):.2f}"],
        ["Other Charges",     f"Rs. {bill_data.get('other_charges', 0):.2f}"],
        ["Discount",          f"- Rs. {bill_data.get('discount', 0):.2f}"],
        ["Tax",               f"Rs. {bill_data.get('tax', 0):.2f}%"],
    ]

    charges_table = Table(charges, colWidths=["70%", "30%"])
    charges_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  PRIMARY_COLOR),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("BACKGROUND",    (0, 1), (-1, -1), LIGHT_GRAY),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("ALIGN",         (1, 0), (1, -1),  "RIGHT"),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    elements.append(charges_table)
    elements.append(Spacer(1, 8))

    # Total amount
    total_data = [
        ["Total Amount",   f"Rs. {bill_data.get('total_amount', 0):.2f}"],
        ["Paid Amount",    f"Rs. {bill_data.get('paid_amount', 0):.2f}"],
        ["Balance Due",    f"Rs. {bill_data.get('balance_due', 0):.2f}"],
        ["Payment Method", str(bill_data.get("payment_method", "-")).upper()],
        ["Status",         str(bill_data.get("status", "-")).upper()],
    ]

    total_table = Table(total_data, colWidths=["70%", "30%"])
    total_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  SECONDARY_COLOR),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("BACKGROUND",    (0, 1), (-1, -1), colors.HexColor("#f0f9ff")),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#bfdbfe")),
        ("ALIGN",         (1, 0), (1, -1),  "RIGHT"),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("FONTNAME",      (0, 2), (-1, 2),  "Helvetica-Bold"),
        ("TEXTCOLOR",     (0, 2), (-1, 2),  ACCENT_COLOR),
    ]))
    elements.append(total_table)

    elements += build_footer(styles)
    doc.build(elements)
    print(f"Bill report generated: {filepath}")
    return filepath


# ═══════════════════════════════════════════
# REPORT 3: PRESCRIPTION REPORT
# ═══════════════════════════════════════════

def generate_prescription_report(
    prescriptions: list,
    patient_data: dict,
    doctor_data: dict
) -> str:
    filename = f"prescription_{patient_data.get('id', 'new')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        rightMargin=1.5 * cm, leftMargin=1.5 * cm,
        topMargin=1.5 * cm,   bottomMargin=1.5 * cm
    )

    styles   = get_styles()
    elements = []

    elements += build_header(styles, "PRESCRIPTION REPORT")

    # Patient and Doctor info side by side
    pat_doc_table = Table(
        [[
            [
                Paragraph("PATIENT", styles["label"]),
                Paragraph(
                    f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}",
                    styles["value"]
                ),
                Paragraph(f"ID: {patient_data.get('id', '-')}", styles["label"]),
                Paragraph(f"Phone: {patient_data.get('phone', '-')}", styles["label"]),
                Paragraph(f"Blood: {patient_data.get('blood_group', '-')}", styles["label"]),
            ],
            [
                Paragraph("PRESCRIBED BY", styles["label"]),
                Paragraph(
                    f"Dr. {doctor_data.get('first_name', '')} {doctor_data.get('last_name', '')}",
                    styles["value"]
                ),
                Paragraph(doctor_data.get("specialization", "-"), styles["label"]),
                Paragraph(f"Lic: {doctor_data.get('license_number', '-')}", styles["label"]),
                Paragraph(f"Date: {datetime.now().strftime('%d-%m-%Y')}", styles["label"]),
            ]
        ]],
        colWidths=["50%", "50%"]
    )
    pat_doc_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, 0), LIGHT_BLUE),
        ("BACKGROUND",    (1, 0), (1, 0), colors.HexColor("#dcfce7")),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
    ]))
    elements.append(pat_doc_table)
    elements.append(Spacer(1, 12))

    # Medicines table
    elements.append(Paragraph("Prescribed Medicines", styles["section_title"]))

    med_rows = [["#", "Medicine", "Dosage", "Frequency", "Duration", "Instructions"]]
    for i, rx in enumerate(prescriptions, 1):
        med_rows.append([
            str(i),
            rx.get("medicine_name", "-"),
            rx.get("dosage", "-"),
            rx.get("frequency", "-"),
            f"{rx.get('duration_days', '-')} days",
            rx.get("instructions", "-"),
        ])

    med_table = Table(
        med_rows,
        colWidths=["5%", "25%", "12%", "18%", "12%", "28%"]
    )
    med_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  PRIMARY_COLOR),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("ALIGN",         (1, 0), (1, -1),  "LEFT"),
        ("ALIGN",         (5, 0), (5, -1),  "LEFT"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ]))
    elements.append(med_table)
    elements.append(Spacer(1, 20))

    # Signature
    sig = Table(
        [["", "Doctor's Signature & Stamp"]],
        colWidths=["50%", "50%"]
    )
    sig.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 40),
        ("ALIGN",         (1, 0), (1, 0),   "CENTER"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("TEXTCOLOR",     (0, 0), (-1, -1), colors.HexColor("#666666")),
        ("LINEABOVE",     (1, 0), (1, 0),   1, colors.HexColor("#aaaaaa")),
    ]))
    elements.append(sig)

    elements += build_footer(styles)
    doc.build(elements)
    print(f"Prescription report generated: {filepath}")
    return filepath


# ═══════════════════════════════════════════
# REPORT 4: LAB REPORT
# ═══════════════════════════════════════════

def generate_lab_report(
    lab_reports: list,
    patient_data: dict
) -> str:
    filename = f"lab_report_{patient_data.get('id', 'new')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        rightMargin=1.5 * cm, leftMargin=1.5 * cm,
        topMargin=1.5 * cm,   bottomMargin=1.5 * cm
    )

    styles   = get_styles()
    elements = []

    elements += build_header(styles, "LAB REPORT")

    # Patient info
    elements.append(Paragraph("Patient Information", styles["section_title"]))
    pat_info = [
        ("Patient Name", f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}"),
        ("Patient ID",   str(patient_data.get("id", "-"))),
        ("Phone",        patient_data.get("phone", "-")),
        ("Blood Group",  patient_data.get("blood_group", "-")),
        ("Gender",       patient_data.get("gender", "-")),
        ("Report Date",  datetime.now().strftime("%d-%m-%Y")),
    ]
    elements.append(info_table(pat_info, styles))
    elements.append(Spacer(1, 12))

    # Lab results table
    elements.append(Paragraph("Test Results", styles["section_title"]))

    lab_rows = [["#", "Test Name", "Type", "Result", "Reference Range", "Status"]]
    for i, lab in enumerate(lab_reports, 1):
        is_abnormal = lab.get("is_abnormal", False)
        status      = "ABNORMAL" if is_abnormal else "NORMAL"
        lab_rows.append([
            str(i),
            lab.get("test_name", "-"),
            lab.get("test_type", "-"),
            lab.get("result", "-"),
            lab.get("reference_range", "-"),
            status,
        ])

    lab_table = Table(
        lab_rows,
        colWidths=["5%", "22%", "15%", "22%", "22%", "14%"]
    )

    style_cmds = [
        ("BACKGROUND",    (0, 0), (-1, 0),  PRIMARY_COLOR),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("ALIGN",         (1, 0), (1, -1),  "LEFT"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ]

    # Highlight abnormal results in red
    for i, lab in enumerate(lab_reports, 1):
        if lab.get("is_abnormal", False):
            style_cmds.append(
                ("TEXTCOLOR", (5, i), (5, i), ACCENT_COLOR)
            )
            style_cmds.append(
                ("FONTNAME", (5, i), (5, i), "Helvetica-Bold")
            )

    lab_table.setStyle(TableStyle(style_cmds))
    elements.append(lab_table)

    elements.append(Spacer(1, 20))

    # Lab technician signature
    sig = Table(
        [["Pathologist Signature", "Lab Technician Signature"]],
        colWidths=["50%", "50%"]
    )
    sig.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 40),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("TEXTCOLOR",     (0, 0), (-1, -1), colors.HexColor("#666666")),
        ("LINEABOVE",     (0, 0), (-1, -1), 1, colors.HexColor("#aaaaaa")),
    ]))
    elements.append(sig)

    elements += build_footer(styles)
    doc.build(elements)
    print(f"Lab report generated: {filepath}")
    return filepath