from unittest.mock import patch, MagicMock

@patch("app.main.BlobServiceClient")
def test_index_route(mock_blob_service):
    mock_blob_instance = MagicMock()
    mock_blob_instance.get_container_client.return_value.list_blobs.return_value = []
    mock_blob_service.from_connection_string.return_value = mock_blob_instance

    from app.main import app  # Jetzt importieren, nachdem BlobServiceClient gepatcht ist
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
