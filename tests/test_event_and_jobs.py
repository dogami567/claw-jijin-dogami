from datetime import date

from fastapi.testclient import TestClient

from claw_jijin_dogami.api.app import create_app
from claw_jijin_dogami.models.fund import FundHistoryPoint, FundPointInTimeResponse


client = TestClient(create_app())


def test_event_impact_endpoint_returns_sorted_impacts() -> None:
    response = client.post(
        "/v1/event/impact",
        json={
            "user_id": "u-1",
            "portfolio_id": "p-1",
            "cutoff_ts": "2025-06-30T20:00:00Z",
            "event": {
                "event_type": "policy",
                "title": "新能源补贴政策调整",
                "published_at": "2025-06-30T10:30:00Z",
                "sentiment_score": -0.8,
                "intensity": 0.9,
                "tags": ["新能源", "政策"],
            },
            "exposures": [
                {
                    "fund_code": "000001",
                    "fund_name": "新能源主题基金",
                    "portfolio_weight": 0.5,
                    "event_exposure": 0.9,
                    "sensitivity": 1.2,
                },
                {
                    "fund_code": "000002",
                    "fund_name": "红利价值基金",
                    "portfolio_weight": 0.5,
                    "event_exposure": 0.1,
                    "sensitivity": 0.8,
                },
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["event_summary"] == "policy: 新能源补贴政策调整"
    assert payload["impacted_funds"][0]["fund_code"] == "000001"
    assert payload["impacted_funds"][0]["direction"] == "negative"
    assert payload["portfolio_impact_score"] < 0


def test_replay_job_creation_and_lookup() -> None:
    create_response = client.post(
        "/v1/jobs/replay",
        json={
            "user_id": "u-2",
            "portfolio_id": "p-2",
            "cutoff_ts": "2025-06-30T20:00:00Z",
            "horizons": [5, 20],
            "benchmark_set": ["buy_hold"],
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()
    assert created["kind"] == "replay"
    assert created["status"] == "completed"

    job_response = client.get(f"/v1/jobs/{created['job_id']}")
    assert job_response.status_code == 200
    job_payload = job_response.json()
    assert job_payload["job_id"] == created["job_id"]
    assert job_payload["result"]["horizons"] == [5, 20]

    result_response = client.get(f"/v1/jobs/{created['job_id']}/result")
    assert result_response.status_code == 200
    result_payload = result_response.json()
    assert result_payload["result"]["benchmark_set"] == ["buy_hold"]


def test_backtest_job_creation_and_result_contract() -> None:
    response = client.post(
        "/v1/jobs/backtest",
        json={
            "user_id": "u-3",
            "portfolio_id": "p-3",
            "strategy_name": "weekly_dca",
            "start_date": "2024-01-01",
            "end_date": "2025-01-01",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["kind"] == "backtest"
    assert payload["status"] == "completed"

    result_response = client.get(f"/v1/jobs/{payload['job_id']}/result")
    assert result_response.status_code == 200
    result_payload = result_response.json()
    assert result_payload["result"]["strategy_name"] == "weekly_dca"


def test_replay_job_embeds_point_in_time_nav_context(monkeypatch) -> None:
    from claw_jijin_dogami.services import jobs as jobs_service

    def fake_point_in_time_nav(request):
        return FundPointInTimeResponse(
            provider_requested=request.provider,
            provider_used="efinance",
            symbol=request.symbol,
            cutoff_date=request.cutoff_date,
            lookback_days=request.lookback_days,
            point=FundHistoryPoint(date=date(2025, 6, 30), unit_nav=1.234),
        )

    monkeypatch.setattr(jobs_service, "get_point_in_time_nav", fake_point_in_time_nav)

    create_response = client.post(
        "/v1/jobs/replay",
        json={
            "user_id": "u-4",
            "portfolio_id": "p-4",
            "cutoff_ts": "2025-06-30T20:00:00Z",
            "horizons": [5, 20],
            "benchmark_set": ["buy_hold"],
            "fund_symbols": ["000001", "000002"],
            "provider": "efinance",
            "lookback_days": 15,
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()

    result_response = client.get(f"/v1/jobs/{created['job_id']}/result")
    assert result_response.status_code == 200
    result_payload = result_response.json()
    assert result_payload["result"]["fund_symbols"] == ["000001", "000002"]
    assert result_payload["result"]["provider"] == "efinance"
    assert result_payload["result"]["lookback_days"] == 15
    assert len(result_payload["result"]["observed_navs"]) == 2
    assert result_payload["result"]["observed_navs"][0]["point"]["unit_nav"] == 1.234
    assert result_payload["result"]["nav_errors"] == []
