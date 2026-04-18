from fastapi.testclient import TestClient

from src.main import app


def test_status_endpoint():
    client = TestClient(app)
    response = client.get("/api/status")

    assert response.status_code == 200
    assert "vector_count" in response.json()
    assert "embedding_model" in response.json()
    assert "openai_enabled" in response.json()
    assert "index_type" in response.json()
