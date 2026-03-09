from fastapi.testclient import TestClient

from claw_jijin_dogami.api.app import create_app


client = TestClient(create_app())


def test_render_portfolio_for_onebot_is_compact() -> None:
    response = client.post(
        "/v1/integrations/clawdbot/render",
        json={
            "channel_type": "onebot",
            "target": "portfolio_analysis",
            "payload": {
                "summary": {
                    "holding_count": 3,
                    "unrealized_pnl": 120.5,
                    "top_holding_fund_code": "000001",
                },
                "recommendation": {"action": "hold"},
                "alerts": [{"message": "单基金仓位过高"}],
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["detail_level"] == "compact"
    assert payload["title"] == "组合分析结果"
    assert any("建议动作" in line for line in payload["bullets"])


def test_render_job_status_for_web_is_full() -> None:
    response = client.post(
        "/v1/integrations/clawdbot/render",
        json={
            "channel_type": "web",
            "target": "job_status",
            "payload": {
                "job_id": "replay-123",
                "kind": "replay",
                "status": "completed",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["detail_level"] == "full"
    assert any("任务编号" in line for line in payload["bullets"])
