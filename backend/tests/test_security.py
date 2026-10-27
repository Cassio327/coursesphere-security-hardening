from unittest.mock import patch


def test_protected_query_rejects_missing_token(client):
    response = client.post("/users/query", json={"query": "show my courses"})

    assert response.status_code == 401
    assert response.json["error"]["code"] == "authentication_required"


def test_token_in_query_string_is_not_accepted(client):
    response = client.get(
        "/users/info?id_token=test-token-not-a-secret"
    )

    assert response.status_code == 401


def test_valid_bearer_token_allows_query(client, valid_authorization):
    with patch("endpoints.Firebase.verify_id_token", return_value={"uid": "user-1"}), patch(
        "endpoints.Firebase.get_user_info", return_value={}
    ):
        response = client.post(
            "/users/query",
            json={"query": "show my courses"},
            headers=valid_authorization,
        )

    assert response.status_code == 200
    assert response.json["botResponse"] == "Fake implementation"


def test_internal_exception_is_not_exposed(client):
    with patch(
        "endpoints.Firebase.create_user",
        side_effect=RuntimeError("private credential path: /secret/file.json"),
    ):
        response = client.post(
            "/users/create",
            json={"email": "candidate@example.com", "password": "long-password"},
        )

    body = response.get_data(as_text=True)
    assert response.status_code == 503
    assert "private credential path" not in body
    assert "/secret/file.json" not in body


def test_cors_allows_only_configured_origin(client):
    allowed = client.get("/health", headers={"Origin": "http://allowed.test"})
    denied = client.get("/health", headers={"Origin": "https://attacker.example"})

    assert allowed.headers["Access-Control-Allow-Origin"] == "http://allowed.test"
    assert "Access-Control-Allow-Origin" not in denied.headers


def test_security_headers_are_returned(client):
    response = client.get("/health")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    assert response.headers["Referrer-Policy"] == "no-referrer"


def test_user_creation_is_rate_limited(client):
    with patch(
        "endpoints.Firebase.create_user",
        return_value={"message": "created", "user_id": "user-1"},
    ):
        first = client.post(
            "/users/create",
            json={"email": "one@example.com", "password": "long-password"},
        )
        second = client.post(
            "/users/create",
            json={"email": "two@example.com", "password": "long-password"},
        )
        third = client.post(
            "/users/create",
            json={"email": "three@example.com", "password": "long-password"},
        )

    assert first.status_code == 201
    assert second.status_code == 201
    assert third.status_code == 429
