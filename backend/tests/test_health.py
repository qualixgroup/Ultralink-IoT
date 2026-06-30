import app.main as main_module


def test_health_is_simple_and_fast(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_full_health_returns_ok_when_dependencies_are_connected(client, monkeypatch):
    async def fake_thingsboard_check() -> dict[str, str]:
        return {"status": "ok"}

    monkeypatch.setattr(main_module, "_check_database", lambda: {"status": "ok"})
    monkeypatch.setattr(main_module, "_check_redis", lambda: {"status": "ok"})
    monkeypatch.setattr(main_module, "_check_thingsboard", fake_thingsboard_check)

    response = client.get("/health/full")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_full_health_returns_503_when_a_dependency_fails(client, monkeypatch):
    async def fake_thingsboard_check() -> dict[str, str]:
        return {"status": "ok"}

    monkeypatch.setattr(main_module, "_check_database", lambda: {"status": "ok"})
    monkeypatch.setattr(main_module, "_check_redis", lambda: {"status": "error"})
    monkeypatch.setattr(main_module, "_check_thingsboard", fake_thingsboard_check)

    response = client.get("/health/full")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["redis"]["status"] == "error"
