def test_health_identifies_service_and_instance(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"
    assert response.json["service"] == "coursesphere-backend"
    assert "instance" in response.json


def test_metrics_expose_request_count_and_latency(client):
    client.get("/health")
    response = client.get("/metrics")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "coursesphere_http_requests_total" in body
    assert "coursesphere_http_request_duration_seconds" in body


def test_request_id_is_returned(client):
    response = client.get(
        "/health", headers={"X-Request-ID": "assessment-request-001"}
    )

    assert response.headers["X-Request-ID"] == "assessment-request-001"
