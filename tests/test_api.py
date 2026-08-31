from fastapi.testclient import TestClient

from news_agent.api import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_demo_report_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/demo")
        assert response.status_code == 200
        assert "AI 新闻早报" in response.json()["report"]
