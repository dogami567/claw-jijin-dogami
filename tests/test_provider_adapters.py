from datetime import datetime
from types import SimpleNamespace

from claw_jijin_dogami.providers.efinance import EfinanceProviderAdapter


class FakeFrame:
    def __init__(self, records):
        self._records = records

    def to_dict(self, orient="records"):
        assert orient == "records"
        return list(self._records)


def test_efinance_adapter_normalizes_snapshot_and_history(monkeypatch) -> None:
    adapter = EfinanceProviderAdapter()
    fake_module = SimpleNamespace(
        fund=SimpleNamespace(
            get_base_info=lambda symbols: FakeFrame(
                [
                    {
                        "基金代码": symbols[0],
                        "基金简称": "测试基金",
                        "单位净值": "1.234",
                        "累计净值": "2.468",
                        "日增长率": "0.56%",
                    }
                ]
            ),
            get_quote_history=lambda symbol: FakeFrame(
                [
                    {
                        "日期": "2026-03-07",
                        "单位净值": "1.220",
                        "累计净值": "2.440",
                        "日增长率": "0.11%",
                    },
                    {
                        "日期": "2026-03-08",
                        "单位净值": "1.234",
                        "累计净值": "2.468",
                        "日增长率": "0.56%",
                    },
                ]
            ),
        )
    )
    monkeypatch.setattr(adapter, "load_module", lambda: fake_module)

    snapshot = adapter.fetch_fund_snapshot("000001")
    history = adapter.fetch_fund_history("000001", limit=1)

    assert snapshot.symbol == "000001"
    assert snapshot.fund_name == "测试基金"
    assert snapshot.unit_nav == 1.234
    assert snapshot.accumulated_nav == 2.468
    assert snapshot.daily_change_pct == 0.56
    assert snapshot.as_of == datetime(2026, 3, 8, 0, 0, 0)
    assert len(history) == 1
    assert history[0].date.isoformat() == "2026-03-08"
    assert history[0].unit_nav == 1.234
