
from fpdf import FPDF


def create_notes_pdf(notes):
    """Create a PDF file from the generated study notes."""

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(
        0, 12, "YouTube AI Notes Studio",
        new_x="LMARGIN", new_y="NEXT"
    )

    pdf.ln(5)
    pdf.set_font("Helvetica", size=11)

    # Replace common Unicode punctuation with PDF-safe characters.
    safe_notes = (
        notes.replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2022", "-")
    )

    pdf.multi_cell(0, 7, safe_notes)

    return bytes(pdf.output())
