from fastapi.testclient import TestClient

from claw_jijin_dogami.api.app import create_app


client = TestClient(create_app())


def test_capabilities_endpoint_exposes_supported_contracts() -> None:
    response = client.get("/v1/capabilities")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "claw-jijin-dogami"
    assert payload["version"] == "0.1.0"
    assert "/v1/portfolio/analyze" in payload["sync_endpoints"]
    assert "/v1/fund/search" in payload["sync_endpoints"]
    assert "/v1/fund/nav/point-in-time" in payload["sync_endpoints"]
    assert "replay" in payload["async_job_kinds"]
    assert "onebot" in payload["supported_channels"]
