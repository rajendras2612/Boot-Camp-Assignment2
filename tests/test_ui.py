from fastapi.testclient import TestClient

from src.main import app


def test_ui_page_available():
    client = TestClient(app)
    response = client.get("/app")

    assert response.status_code == 200
    assert "Multimodal RAG Demo" in response.text
