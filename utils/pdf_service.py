
import re
import html
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    ListFlowable,
    ListItem,
)


def markdown_to_reportlab(text):
    """Convert common Markdown inline formatting to ReportLab markup."""

    # Protect inline code before escaping other content.
    code_parts = []

    def save_code(match):
        code_parts.append(match.group(1))
        return f"ZZCODEPLACEHOLDER{len(code_parts) - 1}ZZ"

    text = re.sub(r"`([^`]+)`", save_code, text)

    # Escape HTML/XML special characters.
    text = html.escape(text, quote=False)

    # Bold and italic formatting.
    text = re.sub(
        r"\*\*(.+?)\*\*",
        r"<b>\1</b>",
        text,
    )
    text = re.sub(
        r"(?<!\*)\*([^*\n]+)\*(?!\*)",
        r"<i>\1</i>",
        text,
    )

    # Restore inline code with a styled font.
    for index, code in enumerate(code_parts):
        safe_code = html.escape(code, quote=False)
        text = text.replace(
            f"ZZCODEPLACEHOLDER{index}ZZ",
            f'<font name="Courier">{safe_code}</font>',
        )

    return text


def create_notes_pdf(notes_text):
    """Create a formatted PDF from Markdown-style study notes."""

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title="YouTube AI Study Notes",
        author="YouTube AI Notes Studio",
    )

    # ---------- PDF styles ----------
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "StudyTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=26,
        textColor=colors.HexColor("#6036A5"),
        alignment=TA_CENTER,
        spaceAfter=18,
        keepWithNext=True,
    )

    h1_style = ParagraphStyle(
        "StudyHeading1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=21,
        textColor=colors.HexColor("#6036A5"),
        spaceBefore=15,
        spaceAfter=9,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "StudyHeading2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#7950C7"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True,
    )

    h3_style = ParagraphStyle(
        "StudyHeading3",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#6036A5"),
        spaceBefore=9,
        spaceAfter=5,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "StudyBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#292533"),
        alignment=TA_LEFT,
        spaceAfter=8,
        splitLongWords=1,
    )

    bullet_style = ParagraphStyle(
        "StudyBullet",
        parent=body_style,
        leftIndent=3,
        spaceAfter=5,
    )

    story = []
    bullet_items = []
    numbered_items = []
    numbered_mode = False
    first_heading = True

    def flush_lists():
        nonlocal numbered_mode

        if bullet_items:
            story.append(
                ListFlowable(
                    [
                        ListItem(
                            Paragraph(item, bullet_style),
                            leftIndent=12,
                        )
                        for item in bullet_items
                    ],
                    bulletType="bullet",
                    start="circle",
                    leftIndent=18,
                    bulletFontName="Helvetica",
                    bulletFontSize=7,
                    bulletColor=colors.HexColor("#7950C7"),
                    spaceAfter=8,
                )
            )
            bullet_items.clear()

        if numbered_items:
            story.append(
                ListFlowable(
                    [
                        ListItem(
                            Paragraph(item, bullet_style),
                            leftIndent=12,
                        )
                        for item in numbered_items
                    ],
                    bulletType="1",
                    start="1",
                    leftIndent=22,
                    bulletFontName="Helvetica",
                    bulletFontSize=9,
                    bulletColor=colors.HexColor("#6036A5"),
                    spaceAfter=8,
                )
            )
            numbered_items.clear()

        numbered_mode = False

    # ---------- Parse Markdown line by line ----------
    for raw_line in (notes_text or "").splitlines():
        line = raw_line.strip()

        # Skip blank lines and horizontal separators.
        if not line:
            flush_lists()
            continue

        if re.fullmatch(r"[-*_]{3,}", line):
            flush_lists()
            story.append(
                Spacer(1, 4)
            )
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.7,
                    color=colors.HexColor("#D9C9F2"),
                    spaceBefore=4,
                    spaceAfter=10,
                )
            )
            continue

        # Main and subheadings: #, ##, ###, etc.
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)

        if heading_match:
            flush_lists()

            level = len(heading_match.group(1))
            heading_text = markdown_to_reportlab(
                heading_match.group(2).strip()
            )

            if level == 1 and first_heading:
                story.append(
                    Paragraph(heading_text, title_style)
                )
                first_heading = False
            elif level <= 2:
                story.append(
                    Paragraph(heading_text, h1_style)
                )
            elif level <= 4:
                story.append(
                    Paragraph(heading_text, h2_style)
                )
            else:
                story.append(
                    Paragraph(heading_text, h3_style)
                )

            continue

        # Bullet lists: - item, * item, or + item.
        bullet_match = re.match(r"^\s*[-*+]\s+(.+)$", raw_line)

        if bullet_match:
            if numbered_items:
                flush_lists()

            bullet_items.append(
                markdown_to_reportlab(bullet_match.group(1))
            )
            continue

        # Numbered lists: 1. item, 2. item, etc.
        number_match = re.match(r"^\s*\d+[.)]\s+(.+)$", raw_line)

        if number_match:
            if bullet_items:
                flush_lists()

            numbered_items.append(
                markdown_to_reportlab(number_match.group(1))
            )
            numbered_mode = True
            continue

        # Normal paragraph.
        flush_lists()

        story.append(
            Paragraph(
                markdown_to_reportlab(line),
                body_style,
            )
        )

    flush_lists()

    # Build the PDF.
    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes