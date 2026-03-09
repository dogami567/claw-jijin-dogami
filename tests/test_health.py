from fastapi.testclient import TestClient

from claw_jijin_dogami.api.app import create_app


client = TestClient(create_app())


def test_root_returns_service_metadata() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"service": "claw-jijin-dogami", "status": "ok"}


def test_healthz_returns_ok() -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
