from datetime import datetime

from fastapi.testclient import TestClient

from claw_jijin_dogami.api.app import create_app
from claw_jijin_dogami.models.portfolio import PortfolioAnalyzeRequest, PortfolioHoldingInput
from claw_jijin_dogami.services.portfolio import analyze_portfolio


client = TestClient(create_app())


def test_analyze_portfolio_service_computes_summary_and_alerts() -> None:
    request = PortfolioAnalyzeRequest(
        user_id="u-1",
        portfolio_id="p-1",
        cutoff_ts=datetime(2025, 6, 30, 20, 0, 0),
        holdings=[
            PortfolioHoldingInput(
                fund_code="000001",
                fund_name="示例成长基金",
                shares=100.0,
                cost_amount=1000.0,
                market_value=1300.0,
                daily_pnl=25.0,
            ),
            PortfolioHoldingInput(
                fund_code="000002",
                fund_name="示例红利基金",
                shares=50.0,
                cost_amount=700.0,
                market_value=600.0,
                daily_pnl=-5.0,
            ),
        ],
        cash_amount=200.0,
    )

    result = analyze_portfolio(request)

    assert result.summary.total_market_value == 1900.0
    assert result.summary.total_cost == 1700.0
    assert result.summary.unrealized_pnl == 200.0
    assert result.summary.unrealized_return_rate == 0.117647
    assert result.summary.top_holding_fund_code == "000001"
    assert result.summary.top_holding_weight == 0.684211
    assert any(alert.code == "holding_concentration" for alert in result.alerts)
    assert result.recommendation.action == "review"


def test_analyze_portfolio_endpoint_returns_contract() -> None:
    response = client.post(
        "/v1/portfolio/analyze",
        json={
            "user_id": "u-2",
            "portfolio_id": "p-2",
            "cutoff_ts": "2025-06-30T20:00:00",
            "cash_amount": 100,
            "holdings": [
                {
                    "fund_code": "000003",
                    "fund_name": "均衡基金",
                    "shares": 10,
                    "cost_amount": 1000,
                    "market_value": 900,
                    "daily_pnl": -10,
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["user_id"] == "u-2"
    assert payload["summary"]["holding_count"] == 1
    assert payload["summary"]["unrealized_pnl"] == -100.0
    assert payload["recommendation"]["action"] == "review"
    assert any(alert["code"] == "drawdown_attention" for alert in payload["alerts"])
