import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ResearchPilot"
    assert "available_models" in data

def test_start_research_validation():
    # Empty query should return 400
    response = client.post("/research", json={"query": "  ", "max_papers": 3})
    assert response.status_code == 400

def test_direct_paper_analysis():
    response = client.post("/papers/analyze", json={
        "text_content": "We propose a novel multi-agent consensus algorithm for agentic retrieval augmented generation.",
        "arxiv_id": "test.2501.0001"
    })
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
    assert "experiments" in data
    assert "critical_review" in data
