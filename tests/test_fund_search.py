from fastapi.testclient import TestClient

from claw_jijin_dogami.api.app import create_app
from claw_jijin_dogami.models.fund import FundSearchCandidate
from claw_jijin_dogami.models.providers import ProviderCapabilities, ProviderStatus


class FakeSearchProvider:
    def __init__(self, name: str, *, available: bool = True, candidates=None) -> None:
        self.name = name
        self._available = available
        self.capabilities = ProviderCapabilities(fund_catalog=True)
        self._candidates = candidates or []

    def is_available(self) -> bool:
        return self._available

    def unavailable_detail(self) -> str | None:
        return f"{self.name} unavailable"

    def build_status(self) -> ProviderStatus:
        return ProviderStatus(
            name=self.name,
            available=self._available,
            capabilities=self.capabilities,
            detail=None if self._available else self.unavailable_detail(),
        )

    def search_funds(self, query: str, limit: int = 10):
        return list(self._candidates)[:limit]


client = TestClient(create_app())


def _patch_registry(monkeypatch, registry):
    from claw_jijin_dogami.providers import registry as provider_registry

    monkeypatch.setattr(provider_registry, "get_provider_registry", lambda: registry)
    monkeypatch.setattr(provider_registry, "DEFAULT_PROVIDER_ORDER", tuple(registry.keys()))


def test_fund_search_endpoint_returns_candidates(monkeypatch) -> None:
    _patch_registry(
        monkeypatch,
        {
            "akshare": FakeSearchProvider(
                "akshare",
                candidates=[
                    FundSearchCandidate(
                        symbol="518880",
                        fund_name="华安黄金ETF",
                        fund_type="ETF",
                        provider="akshare",
                        score=140,
                        match_reason="prefix_name",
                    ),
                    FundSearchCandidate(
                        symbol="159934",
                        fund_name="易方达黄金ETF",
                        fund_type="ETF",
                        provider="akshare",
                        score=100,
                        match_reason="substring_name",
                    ),
                ],
            )
        },
    )

    response = client.post("/v1/fund/search", json={"query": "黄金", "limit": 5})

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider_used"] == "akshare"
    assert payload["candidate_count"] == 2
    assert payload["candidates"][0]["symbol"] == "518880"


def test_fund_search_endpoint_respects_unknown_provider(monkeypatch) -> None:
    _patch_registry(monkeypatch, {"akshare": FakeSearchProvider("akshare")})

    response = client.post("/v1/fund/search", json={"query": "黄金", "provider": "missing"})

    assert response.status_code == 404
    assert "Unknown provider" in response.json()["detail"]
