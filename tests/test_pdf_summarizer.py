from app.pdf_summarizer import extract_text_from_pdf
from io import BytesIO
from reportlab.pdfgen import canvas

def test_extract_text_from_pdf():
    # Erzeuge ein einfaches PDF mit Text "Hello PDF"
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, "Hello PDF")
    c.save()
    buffer.seek(0)

    pdf_bytes = buffer.read()
    text = extract_text_from_pdf(pdf_bytes)

    assert "Hello PDF" in text
