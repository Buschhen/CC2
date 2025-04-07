from unittest.mock import patch
from app.pdf_summarizer import summarize_pdf

@patch("pdf_summarizer.OpenAI")
def test_summarize_pdf_with_mock(mock_openai):
    mock_instance = mock_openai.return_value
    mock_instance.chat.completions.create.return_value = {
        "choices": [{"message": {"content": "Test-Summary"}}]
    }

    text = "Fake PDF content."
    result = summarize_pdf(text)
    assert "Test-Summary" in result
