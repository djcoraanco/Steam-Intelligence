import subprocess
import sys
import os
import pytest
from fastapi.testclient import TestClient


def test_metrics_endpoint(client: TestClient):
    resp = client.get("/api/v1/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "metrics" in data
    assert "indexed_games_count" in data["metrics"]
    assert "total_exports_count" in data["metrics"]


def test_readiness_and_health_checks(client: TestClient):
    ready_resp = client.get("/api/v1/ready")
    assert ready_resp.status_code == 200
    assert ready_resp.json()["ready"] is True

    health_resp = client.get("/api/v1/health")
    assert health_resp.status_code == 200
    h_data = health_resp.json()
    assert h_data["status"] in ["ok", "healthy"]
    assert "database" in h_data["components"]
    assert "steam_provider" in h_data["components"]


def test_restore_verification_script():
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "restore_test.py"))
    assert os.path.exists(script_path)
    res = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    assert res.returncode == 0
    assert "All required core and phase tables verified" in res.stdout
