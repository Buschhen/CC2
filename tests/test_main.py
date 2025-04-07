from unittest.mock import patch, MagicMock
from app.main import app

@patch("app.main.container_client")
def test_index_route(mock_container_client):
    mock_container_client.list_blobs.return_value = []

    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
