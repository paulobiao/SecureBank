from fastapi.testclient import TestClient
from src.securebank.main import app

def test_score_endpoint():
    c = TestClient(app)
    r = c.post("/api/v1/score", json={"user_id":"u","amount":600,"merchant":"ELC","ip":"198.51.100.20","device_id":"d"})
    assert r.status_code == 200
    j = r.json()
    assert "score" in j and "reasons" in j
    assert j["score"] <= 100
