def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "degraded"]
    assert data["version"] == "1.0.0"
    assert "components" in data
    assert "database" in data["components"]
    assert data["components"]["database"]["status"] == "healthy"


def test_readiness_check(client):
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json() == {"ready": True}


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"
