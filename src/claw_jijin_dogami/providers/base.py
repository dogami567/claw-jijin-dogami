from __future__ import annotations

from datetime import date, datetime
from importlib import import_module
from typing import Any

from claw_jijin_dogami.models.fund import FundHistoryPoint, FundLiveSnapshot, FundSearchCandidate
from claw_jijin_dogami.models.providers import ProviderCapabilities, ProviderStatus


class ProviderError(Exception):
    pass


class UnknownProviderError(ProviderError):
    def __init__(self, provider_name: str) -> None:
        super().__init__(f"Unknown provider: {provider_name}")
        self.provider_name = provider_name


class ProviderUnavailableError(ProviderError):
    def __init__(self, provider_name: str, detail: str | None = None) -> None:
        message = f"Provider '{provider_name}' is unavailable"
        if detail:
            message = f"{message}: {detail}"
        super().__init__(message)
        self.provider_name = provider_name
        self.detail = detail


class ProviderCapabilityError(ProviderError):
    def __init__(self, provider_name: str, capability: str) -> None:
        super().__init__(f"Provider '{provider_name}' does not support capability '{capability}'")
        self.provider_name = provider_name
        self.capability = capability


class ProviderDataError(ProviderError):
    def __init__(self, provider_name: str, detail: str) -> None:
        super().__init__(f"Provider '{provider_name}' data error: {detail}")
        self.provider_name = provider_name
        self.detail = detail


class BaseProviderAdapter:
    name = "base"
    module_name: str | None = None
    capabilities = ProviderCapabilities()

    def __init__(self) -> None:
        self._module_loaded = False
        self._module: Any | None = None

    def load_module(self) -> Any | None:
        if self._module_loaded:
            return self._module

        self._module_loaded = True
        if self.module_name is None:
            return None

        try:
            self._module = import_module(self.module_name)
        except ImportError:
            self._module = None

        return self._module

    def is_available(self) -> bool:
        return self.load_module() is not None

    def unavailable_detail(self) -> str | None:
        if self.module_name is None:
            return "no backing python module configured"
        return f"python package '{self.module_name}' is not installed"

    def status_detail(self) -> str | None:
        if self.is_available():
            return None
        return self.unavailable_detail()

    def build_status(self) -> ProviderStatus:
        return ProviderStatus(
            name=self.name,
            available=self.is_available(),
            capabilities=self.capabilities,
            detail=self.status_detail(),
        )

    def require_available(self) -> Any:
        module = self.load_module()
        if module is None:
            raise ProviderUnavailableError(self.name, self.unavailable_detail())
        return module

    def fetch_fund_snapshot(self, symbol: str) -> FundLiveSnapshot:
        raise ProviderCapabilityError(self.name, "live_snapshot")

    def fetch_fund_history(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int | None = None,
    ) -> list[FundHistoryPoint]:
        raise ProviderCapabilityError(self.name, "historical_nav")

    def search_funds(self, query: str, limit: int = 10) -> list[FundSearchCandidate]:
        raise ProviderCapabilityError(self.name, "fund_catalog")


def records_from_tabular(payload: Any) -> list[dict[str, Any]]:
    if payload is None:
        return []
    if isinstance(payload, dict):
        return [payload]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    to_dict = getattr(payload, "to_dict", None)
    if callable(to_dict):
        try:
            records = to_dict(orient="records")
        except TypeError:
            records = to_dict("records")
        if isinstance(records, list):
            return [item for item in records if isinstance(item, dict)]

    return []


def is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() in {"", "--", "N/A", "nan", "None", "null"}:
        return True
    return False


def first_present(*values: Any) -> Any:
    for value in values:
        if not is_missing(value):
            return value
    return None


def pick_field(record: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = record.get(key)
        if not is_missing(value):
            return value
    return None


def to_float(value: Any) -> float | None:
    if is_missing(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        if cleaned.endswith("%"):
            cleaned = cleaned[:-1]
        try:
            return float(cleaned)
        except ValueError:
            return None

    return None


def to_datetime(value: Any) -> datetime | None:
    if is_missing(value):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())

    to_pydatetime = getattr(value, "to_pydatetime", None)
    if callable(to_pydatetime):
        converted = to_pydatetime()
        if isinstance(converted, datetime):
            return converted

    if isinstance(value, str):
        text = value.strip()
        for candidate in (text, text.replace("/", "-"), text.replace(".", "-")):
            try:
                return datetime.fromisoformat(candidate)
            except ValueError:
                continue

    return None


def to_date(value: Any) -> date | None:
    normalized = to_datetime(value)
    if normalized is not None:
        return normalized.date()
    if isinstance(value, date):
        return value
    return None
