from types import SimpleNamespace

from claw_jijin_dogami.providers.akshare import AkshareProviderAdapter


class FakeFrame:
    def __init__(self, records):
        self._records = records

    def to_dict(self, orient="records"):
        assert orient == "records"
        return list(self._records)


def test_akshare_adapter_searches_funds_by_name_and_code(monkeypatch) -> None:
    adapter = AkshareProviderAdapter()
    fake_module = SimpleNamespace(
        fund_name_em=lambda: FakeFrame(
            [
                {"基金代码": "518880", "基金简称": "华安黄金ETF", "基金类型": "ETF"},
                {"基金代码": "159934", "基金简称": "易方达黄金ETF", "基金类型": "ETF"},
                {"基金代码": "161725", "基金简称": "招商中证白酒指数(LOF)A", "基金类型": "指数"},
            ]
        )
    )
    monkeypatch.setattr(adapter, "load_module", lambda: fake_module)

    candidates = adapter.search_funds("黄金", limit=5)
    by_code = adapter.search_funds("159934", limit=5)

    assert [candidate.symbol for candidate in candidates] == ["518880", "159934"]
    assert all(candidate.match_reason in {"substring_name", "prefix_name", "exact_name"} for candidate in candidates)
    assert by_code[0].symbol == "159934"
    assert by_code[0].match_reason == "exact_symbol"
