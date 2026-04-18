from fastapi.testclient import TestClient
from src.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Multimodal RAG API is running"


def test_docs_landing():
    response = client.get("/docs")

    assert response.status_code == 200
    assert "API Documentation" in response.text
    assert "/docs/swagger" in response.text


def test_query_requires_body():
    response = client.post("/query", json={})
    assert response.status_code == 422
