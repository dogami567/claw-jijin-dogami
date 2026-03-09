from fastapi.testclient import TestClient

from claw_jijin_dogami.api.app import create_app


client = TestClient(create_app())


def test_replay_context_filters_future_records() -> None:
    response = client.post(
        "/v1/replay/context",
        json={
            "user_id": "u-1",
            "portfolio_id": "p-1",
            "cutoff_ts": "2025-06-30T20:00:00Z",
            "snapshots": [
                {
                    "record_id": "s-1",
                    "record_type": "fund_snapshot",
                    "target_code": "000001",
                    "published_at": "2025-06-29T20:00:00Z",
                },
                {
                    "record_id": "s-2",
                    "record_type": "fund_snapshot",
                    "target_code": "000001",
                    "published_at": "2025-07-01T09:00:00Z",
                },
            ],
            "events": [
                {
                    "record_id": "e-1",
                    "record_type": "news",
                    "target_code": "新能源",
                    "published_at": "2025-06-30T10:00:00Z",
                },
                {
                    "record_id": "e-2",
                    "record_type": "news",
                    "target_code": "新能源",
                    "published_at": "2025-07-02T10:00:00Z",
                },
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["eligible_snapshot_count"] == 1
    assert payload["eligible_event_count"] == 1
    assert payload["dropped_future_snapshot_count"] == 1
    assert payload["dropped_future_event_count"] == 1
    assert payload["warnings"] == []


def test_replay_context_warns_when_no_eligible_records() -> None:
    response = client.post(
        "/v1/replay/context",
        json={
            "user_id": "u-2",
            "portfolio_id": "p-2",
            "cutoff_ts": "2025-06-30T20:00:00Z",
            "snapshots": [],
            "events": [],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["eligible_snapshot_count"] == 0
    assert payload["eligible_event_count"] == 0
    assert len(payload["warnings"]) == 2
