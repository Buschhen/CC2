from unittest.mock import patch, MagicMock
from app.pdf_summarizer import summarize_pdf

@patch("app.pdf_summarizer.OpenAI")  # <- korrektes Patch-Ziel
def test_summarize_pdf_with_mock(mock_openai_class):
    # Setup fake OpenAI client
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = {
        "choices": [{"message": {"content": "Fake summary"}}]
    }
    mock_openai_class.return_value = mock_client

    result = summarize_pdf("This is dummy PDF content.")
    assert "Fake summary" in result
