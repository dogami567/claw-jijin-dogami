from fastapi.testclient import TestClient

from claw_jijin_dogami.api.app import create_app


client = TestClient(create_app())


def test_recommendation_reduces_when_negative_event_and_drawdown_stack() -> None:
    response = client.post(
        "/v1/recommendation/generate",
        json={
            "user_id": "u-1",
            "portfolio_id": "p-1",
            "cutoff_ts": "2025-06-30T20:00:00Z",
            "portfolio_analysis": {
                "user_id": "u-1",
                "portfolio_id": "p-1",
                "cutoff_ts": "2025-06-30T20:00:00Z",
                "summary": {
                    "total_market_value": 900,
                    "total_cost": 1100,
                    "cash_amount": 100,
                    "unrealized_pnl": -200,
                    "unrealized_return_rate": -0.181818,
                    "daily_pnl": -20,
                    "holding_count": 1,
                    "top_holding_fund_code": "000001",
                    "top_holding_weight": 1.0,
                },
                "alerts": [
                    {
                        "code": "drawdown_attention",
                        "severity": "warn",
                        "message": "组合浮动亏损超过 10%",
                    }
                ],
                "recommendation": {
                    "action": "review",
                    "rationale": "先复核",
                },
            },
            "event_impact": {
                "user_id": "u-1",
                "portfolio_id": "p-1",
                "cutoff_ts": "2025-06-30T20:00:00Z",
                "event_summary": "policy: 利空政策",
                "portfolio_impact_score": -0.22,
                "confidence": 0.8,
                "impacted_funds": [],
                "reasoning_summary": "test",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["recommendation"]["action"] == "reduce"
    assert payload["recommendation"]["score"] < 0
    assert "negative_event" in payload["recommendation"]["risk_flags"]


def test_recommendation_can_suggest_add_when_positive_without_risk_flags() -> None:
    response = client.post(
        "/v1/recommendation/generate",
        json={
            "user_id": "u-2",
            "portfolio_id": "p-2",
            "cutoff_ts": "2025-06-30T20:00:00Z",
            "portfolio_analysis": {
                "user_id": "u-2",
                "portfolio_id": "p-2",
                "cutoff_ts": "2025-06-30T20:00:00Z",
                "summary": {
                    "total_market_value": 1180,
                    "total_cost": 1000,
                    "cash_amount": 200,
                    "unrealized_pnl": 180,
                    "unrealized_return_rate": 0.18,
                    "daily_pnl": 15,
                    "holding_count": 2,
                    "top_holding_fund_code": "000002",
                    "top_holding_weight": 0.35,
                },
                "alerts": [],
                "recommendation": {
                    "action": "hold",
                    "rationale": "保持纪律",
                },
            },
            "event_impact": {
                "user_id": "u-2",
                "portfolio_id": "p-2",
                "cutoff_ts": "2025-06-30T20:00:00Z",
                "event_summary": "macro: 宽松信号",
                "portfolio_impact_score": 0.18,
                "confidence": 0.85,
                "impacted_funds": [],
                "reasoning_summary": "test",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["recommendation"]["action"] == "add"
    assert payload["recommendation"]["score"] > 0
    assert payload["recommendation"]["confidence"] >= 0.7
