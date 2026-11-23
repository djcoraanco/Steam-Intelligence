def test_auth_workflow(client):
    # 1. First user registers (should be automatically assigned 'owner')
    reg_resp = client.post("/api/v1/auth/register", json={
        "email": "owner@steamintel.internal",
        "password": "SuperSecretPassword123!",
        "display_name": "Admin Owner"
    })
    assert reg_resp.status_code == 201
    user_data = reg_resp.json()
    assert user_data["email"] == "owner@steamintel.internal"
    assert "owner" in user_data["roles"]

    # 2. Duplicate registration should fail
    dup_resp = client.post("/api/v1/auth/register", json={
        "email": "owner@steamintel.internal",
        "password": "AnotherPassword123!"
    })
    assert dup_resp.status_code == 400

    # 3. Second user registers (should receive specified role)
    analyst_resp = client.post("/api/v1/auth/register", json={
        "email": "analyst@steamintel.internal",
        "password": "AnalystPassword123!",
        "display_name": "Senior Analyst",
        "role": "analyst"
    })
    assert analyst_resp.status_code == 201
    assert "analyst" in analyst_resp.json()["roles"]

    # 4. Login with bad credentials should fail
    bad_login = client.post("/api/v1/auth/login", json={
        "email": "owner@steamintel.internal",
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401

    # 5. Login with good credentials should succeed and return access token
    good_login = client.post("/api/v1/auth/login", json={
        "email": "owner@steamintel.internal",
        "password": "SuperSecretPassword123!"
    })
    assert good_login.status_code == 200
    token_data = good_login.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert "owner" in token_data["roles"]

    token = token_data["access_token"]

    # 6. Call /api/v1/auth/me without token -> 401
    unauth_resp = client.get("/api/v1/auth/me")
    assert unauth_resp.status_code == 401

    # 7. Call /api/v1/auth/me with Bearer token -> 200
    auth_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert auth_resp.status_code == 200
    me_data = auth_resp.json()
    assert me_data["email"] == "owner@steamintel.internal"
    assert "owner" in me_data["roles"]
