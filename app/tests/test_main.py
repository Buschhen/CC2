from main import app
from unittest.mock import patch, MagicMock
from io import BytesIO

def test_upload_file_mocked():
    client = app.test_client()
    dummy_file = (BytesIO(b"Test PDF content"), "test.pdf")

    with patch("main.blob_client") as mock_blob_client:
        mock_upload = MagicMock()
        mock_blob_client.get_blob_client.return_value = mock_upload

        response = client.post('/upload', data={"file": dummy_file}, content_type='multipart/form-data')
        assert response.status_code == 200
        assert b"Zusammenfassung" in response.data  # je nachdem, was dein Template ausgibt
