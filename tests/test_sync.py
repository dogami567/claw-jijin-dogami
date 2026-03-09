from fastapi.testclient import TestClient

from claw_jijin_dogami.api.app import create_app


client = TestClient(create_app())


def test_sync_plan_builds_tasks_for_core_sources() -> None:
    response = client.post(
        "/v1/sync/plan",
        json={
            "user_id": "u-1",
            "portfolio_id": "p-1",
            "fund_codes": ["000001", "000002", "000001"],
            "as_of": "2025-06-30T20:00:00Z",
            "include_disclosures": True,
            "include_market_events": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    tasks = payload["tasks"]
    assert tasks[0]["provider"] == "xalpha"
    assert tasks[0]["task_type"] == "portfolio_ledger"
    assert any(task["provider"] == "akshare" and task["task_type"] == "fund_snapshot" for task in tasks)
    assert any(task["provider"] == "efinance" and task["task_type"] == "fund_snapshot" for task in tasks)
    assert any(task["task_type"] == "fund_disclosure" for task in tasks)
    assert any(task["task_type"] == "market_event" for task in tasks)
    assert len([task for task in tasks if task["target_code"] == "000001" and task["task_type"] == "fund_snapshot"]) == 2


def test_sync_plan_can_skip_optional_tasks() -> None:
    response = client.post(
        "/v1/sync/plan",
        json={
            "user_id": "u-2",
            "portfolio_id": "p-2",
            "fund_codes": ["000003"],
            "as_of": "2025-06-30T20:00:00Z",
            "include_disclosures": False,
            "include_market_events": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    tasks = payload["tasks"]
    assert not any(task["task_type"] == "fund_disclosure" for task in tasks)
    assert not any(task["task_type"] == "market_event" for task in tasks)
