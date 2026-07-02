"""
Invoice PDF generator using reportlab.
Install: pip install reportlab
"""
import io
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


NAVY  = HexColor("#0B1F3A") if REPORTLAB_AVAILABLE else None
GOLD  = HexColor("#C9A84C") if REPORTLAB_AVAILABLE else None
LIGHT = HexColor("#F5F3EE") if REPORTLAB_AVAILABLE else None


def generate_invoice_pdf(
    invoice_number: str,
    customer_name: str,
    customer_email: str,
    items: list[dict],   # [{"description": str, "amount": int}]
    total_paise: int,
    payment_id: str,
    purpose: str,
) -> bytes:
    """
    Generate a PDF invoice and return it as bytes.

    Args:
        invoice_number: e.g. "INV-2024-0001"
        customer_name: Full name
        customer_email: Email address
        items: List of line items with description + amount (in paise)
        total_paise: Total amount in paise
        payment_id: Razorpay payment ID
        purpose: e.g. "Gold Membership", "Charter Booking"

    Returns:
        PDF as bytes (ready to save or send)
    """
    if not REPORTLAB_AVAILABLE:
        # Return minimal placeholder if reportlab not installed
        return b"%PDF minimal placeholder - install reportlab"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    header_style = ParagraphStyle("header", fontSize=22, textColor=NAVY, fontName="Helvetica-Bold")
    sub_style    = ParagraphStyle("sub",    fontSize=9,  textColor=GOLD,  fontName="Helvetica",  spaceAfter=4)
    story.append(Paragraph("ONENESS AVIATION", header_style))
    story.append(Paragraph("Private Charter &amp; Ferry Flights", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=12))

    # ── Invoice meta ─────────────────────────────────────────────────────────
    meta_data = [
        ["Invoice No.", invoice_number, "Date", datetime.now().strftime("%d %b %Y")],
        ["Payment ID", payment_id,      "Purpose", purpose],
    ]
    meta_table = Table(meta_data, colWidths=[35*mm, 65*mm, 30*mm, 50*mm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME",    (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("FONTNAME",    (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",    (2,0), (2,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",   (0,0), (-1,-1), NAVY),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # ── Bill To ───────────────────────────────────────────────────────────────
    story.append(Paragraph("Bill To", ParagraphStyle("bt_label", fontSize=8, textColor=GOLD, fontName="Helvetica-Bold")))
    story.append(Paragraph(customer_name,  ParagraphStyle("bt_name",  fontSize=11, textColor=NAVY, fontName="Helvetica-Bold")))
    story.append(Paragraph(customer_email, ParagraphStyle("bt_email", fontSize=9,  textColor=NAVY, fontName="Helvetica")))
    story.append(Spacer(1, 14))

    # ── Line items table ──────────────────────────────────────────────────────
    table_data = [["Description", "Amount (INR)"]]
    for item in items:
        rupees = f"₹ {item['amount'] / 100:,.2f}"
        table_data.append([item["description"], rupees])
    table_data.append(["", ""])  # spacer row
    table_data.append(["Total", f"₹ {total_paise / 100:,.2f}"])

    col_widths = [120*mm, 40*mm]
    items_table = Table(table_data, colWidths=col_widths)
    items_table.setStyle(TableStyle([
        # Header row
        ("BACKGROUND",    (0,0),  (-1,0),  NAVY),
        ("TEXTCOLOR",     (0,0),  (-1,0),  white),
        ("FONTNAME",      (0,0),  (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),  (-1,0),  9),
        ("ALIGN",         (1,0),  (1,-1),  "RIGHT"),
        # Body rows
        ("FONTNAME",      (0,1),  (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1),  (-1,-1), 9),
        ("TEXTCOLOR",     (0,1),  (-1,-1), NAVY),
        ("ROWBACKGROUNDS",(0,1),  (-1,-2), [white, LIGHT]),
        ("BOTTOMPADDING", (0,0),  (-1,-1), 6),
        ("TOPPADDING",    (0,0),  (-1,-1), 6),
        # Total row
        ("FONTNAME",      (0,-1), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,-1), (-1,-1), 11),
        ("TEXTCOLOR",     (0,-1), (-1,-1), NAVY),
        ("LINEABOVE",     (0,-1), (-1,-1), 1.5, GOLD),
        ("BACKGROUND",    (0,-1), (-1,-1), LIGHT),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 20))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=GOLD))
    story.append(Spacer(1, 6))
    footer_style = ParagraphStyle("footer", fontSize=8, textColor=HexColor("#888888"), alignment=TA_CENTER)
    story.append(Paragraph(
        "Oneness Aviation · fly@onenessaviation.com · +91 99999 99999 · www.onenessaviation.com",
        footer_style
    ))
    story.append(Paragraph("Thank you for flying with us.", footer_style))

    doc.build(story)
    return buffer.getvalue()
