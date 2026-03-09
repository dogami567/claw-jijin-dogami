from datetime import date, datetime

from fastapi.testclient import TestClient

from claw_jijin_dogami.api.app import create_app
from claw_jijin_dogami.models.fund import FundHistoryPoint, FundLiveSnapshot
from claw_jijin_dogami.models.providers import ProviderCapabilities, ProviderStatus


class FakeProvider:
    def __init__(
        self,
        name: str,
        *,
        available: bool = True,
        capabilities: ProviderCapabilities | None = None,
        snapshot: FundLiveSnapshot | None = None,
        history: list[FundHistoryPoint] | None = None,
        detail: str | None = None,
    ) -> None:
        self.name = name
        self._available = available
        self.capabilities = capabilities or ProviderCapabilities()
        self._snapshot = snapshot
        self._history = history or []
        self._detail = detail

    def is_available(self) -> bool:
        return self._available

    def unavailable_detail(self) -> str | None:
        return self._detail or f"{self.name} unavailable"

    def build_status(self) -> ProviderStatus:
        return ProviderStatus(
            name=self.name,
            available=self._available,
            capabilities=self.capabilities,
            detail=None if self._available else self.unavailable_detail(),
        )

    def fetch_fund_snapshot(self, symbol: str) -> FundLiveSnapshot:
        if self._snapshot is None:
            raise AssertionError("snapshot not configured")
        return self._snapshot.model_copy(update={"symbol": symbol, "provider": self.name})

    def fetch_fund_history(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int | None = None,
    ) -> list[FundHistoryPoint]:
        points = list(self._history)
        if start_date is not None:
            points = [point for point in points if point.date >= start_date]
        if end_date is not None:
            points = [point for point in points if point.date <= end_date]
        if limit is not None:
            points = points[-limit:]
        return points


client = TestClient(create_app())


def _patch_registry(monkeypatch, registry: dict[str, FakeProvider]) -> None:
    from claw_jijin_dogami.providers import registry as provider_registry

    monkeypatch.setattr(provider_registry, "get_provider_registry", lambda: registry)
    monkeypatch.setattr(provider_registry, "DEFAULT_PROVIDER_ORDER", tuple(registry.keys()))


def test_provider_status_endpoint_reflects_availability(monkeypatch) -> None:
    _patch_registry(
        monkeypatch,
        {
            "efinance": FakeProvider(
                "efinance",
                capabilities=ProviderCapabilities(live_snapshot=True, historical_nav=True),
            ),
            "akshare": FakeProvider(
                "akshare",
                available=False,
                capabilities=ProviderCapabilities(fund_catalog=True),
            ),
        },
    )

    response = client.get("/v1/providers/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["default_provider_order"] == ["efinance", "akshare"]
    assert payload["providers"][0]["name"] == "efinance"
    assert payload["providers"][0]["capabilities"]["live_snapshot"] is True
    assert payload["providers"][1]["available"] is False


def test_live_snapshot_uses_requested_provider(monkeypatch) -> None:
    _patch_registry(
        monkeypatch,
        {
            "efinance": FakeProvider(
                "efinance",
                capabilities=ProviderCapabilities(live_snapshot=True),
                snapshot=FundLiveSnapshot(
                    symbol="000001",
                    fund_name="华夏成长",
                    provider="efinance",
                    as_of=datetime(2026, 3, 9, 15, 0, 0),
                    unit_nav=1.234,
                    accumulated_nav=2.345,
                    daily_change_pct=0.45,
                ),
            ),
        },
    )

    response = client.post(
        "/v1/fund/snapshot/live",
        json={"symbol": "000001", "provider": "efinance", "allow_fallback": False},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider_used"] == "efinance"
    assert payload["snapshot"]["fund_name"] == "华夏成长"
    assert payload["snapshot"]["unit_nav"] == 1.234


def test_live_snapshot_falls_back_when_requested_provider_is_unavailable(monkeypatch) -> None:
    _patch_registry(
        monkeypatch,
        {
            "akshare": FakeProvider(
                "akshare",
                available=False,
                capabilities=ProviderCapabilities(fund_catalog=True),
            ),
            "efinance": FakeProvider(
                "efinance",
                capabilities=ProviderCapabilities(live_snapshot=True),
                snapshot=FundLiveSnapshot(
                    symbol="000001",
                    fund_name="华夏成长",
                    provider="efinance",
                    unit_nav=1.111,
                ),
            ),
        },
    )

    response = client.post(
        "/v1/fund/snapshot/live",
        json={"symbol": "000001", "provider": "akshare", "allow_fallback": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider_requested"] == "akshare"
    assert payload["provider_used"] == "efinance"
    assert payload["snapshot"]["unit_nav"] == 1.111


def test_live_snapshot_returns_404_for_unknown_provider(monkeypatch) -> None:
    _patch_registry(
        monkeypatch,
        {
            "efinance": FakeProvider(
                "efinance",
                capabilities=ProviderCapabilities(live_snapshot=True),
            ),
        },
    )

    response = client.post(
        "/v1/fund/snapshot/live",
        json={"symbol": "000001", "provider": "unknown-provider"},
    )

    assert response.status_code == 404
    assert "Unknown provider" in response.json()["detail"]


def test_fund_history_endpoint_returns_filtered_points(monkeypatch) -> None:
    _patch_registry(
        monkeypatch,
        {
            "efinance": FakeProvider(
                "efinance",
                capabilities=ProviderCapabilities(historical_nav=True),
                history=[
                    FundHistoryPoint(date=date(2026, 3, 5), unit_nav=1.10),
                    FundHistoryPoint(date=date(2026, 3, 6), unit_nav=1.11),
                    FundHistoryPoint(date=date(2026, 3, 7), unit_nav=1.12),
                ],
            ),
        },
    )

    response = client.post(
        "/v1/fund/history",
        json={
            "symbol": "000001",
            "provider": "efinance",
            "start_date": "2026-03-06",
            "limit": 1,
            "allow_fallback": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider_used"] == "efinance"
    assert payload["point_count"] == 1
    assert payload["points"][0]["date"] == "2026-03-07"


def test_fund_history_returns_503_when_provider_is_unavailable(monkeypatch) -> None:
    _patch_registry(
        monkeypatch,
        {
            "efinance": FakeProvider(
                "efinance",
                available=False,
                capabilities=ProviderCapabilities(historical_nav=True),
            ),
        },
    )

    response = client.post(
        "/v1/fund/history",
        json={"symbol": "000001", "provider": "efinance", "allow_fallback": False},
    )

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"]
