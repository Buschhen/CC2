from unittest.mock import patch, MagicMock
from app.pdf_summarizer import summarize_pdf

@patch("app.pdf_summarizer.extract_text_from_pdf", return_value="Extracted text from PDF")
@patch("app.pdf_summarizer.OpenAI")
def test_summarize_pdf_with_mock(mock_openai_class, mock_extract):
    mock_openai = MagicMock()
    mock_openai.chat.completions.create.return_value = {
        "choices": [{"message": {"content": "Fake summary"}}]
    }
    mock_openai_class.return_value = mock_openai

    result = summarize_pdf(b"%PDF-1.4...")
    assert "Fake summary" in result
