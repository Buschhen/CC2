from unittest.mock import patch
from app.pdf_summarizer import summarize_pdf

def test_summarize_pdf_with_mock():
    dummy_input = "This is dummy PDF content."

    with patch('pdf_summarizer.openai.ChatCompletion.create') as mock_openai:
        mock_openai.return_value = {
            "choices": [{"message": {"content": "Dies ist eine zusammengefasste Version"}}]
        }

        summary = summarize_pdf(dummy_input)
        assert "zusammengefasste" in summary
