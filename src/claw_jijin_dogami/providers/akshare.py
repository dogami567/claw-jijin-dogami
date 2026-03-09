from claw_jijin_dogami.models.fund import FundSearchCandidate
from claw_jijin_dogami.models.providers import ProviderCapabilities

from .base import BaseProviderAdapter, ProviderDataError, pick_field, records_from_tabular


class AkshareProviderAdapter(BaseProviderAdapter):
    name = "akshare"
    module_name = "akshare"
    capabilities = ProviderCapabilities(
        fund_catalog=True,
    )

    def status_detail(self) -> str | None:
        if self.is_available():
            return "package available; live snapshot and history adapters are not enabled yet"
        return super().status_detail()

    def search_funds(self, query: str, limit: int = 10) -> list[FundSearchCandidate]:
        module = self.require_available()
        fund_name_em = getattr(module, "fund_name_em", None)
        if not callable(fund_name_em):
            raise ProviderDataError(self.name, "missing fund_name_em API")

        try:
            records = records_from_tabular(fund_name_em())
        except Exception as exc:
            raise ProviderDataError(self.name, f"failed to load fund catalog: {exc}") from exc

        normalized_query = query.strip().lower()
        if not normalized_query:
            raise ProviderDataError(self.name, "empty search query")

        scored_candidates: list[FundSearchCandidate] = []
        for record in records:
            symbol = str(pick_field(record, "基金代码", "代码", "symbol") or "").strip()
            fund_name = str(pick_field(record, "基金简称", "基金名称", "名称") or "").strip()
            fund_type = pick_field(record, "基金类型", "类型")
            if not symbol or not fund_name:
                continue

            score, reason = self._score_candidate(
                normalized_query=normalized_query,
                symbol=symbol,
                fund_name=fund_name,
            )
            if score <= 0:
                continue

            scored_candidates.append(
                FundSearchCandidate(
                    symbol=symbol,
                    fund_name=fund_name,
                    fund_type=str(fund_type) if fund_type is not None else None,
                    provider=self.name,
                    score=score,
                    match_reason=reason,
                    raw=record,
                )
            )

        scored_candidates.sort(
            key=lambda candidate: (-candidate.score, candidate.fund_name, candidate.symbol)
        )
        return scored_candidates[:limit]

    def _score_candidate(self, normalized_query: str, symbol: str, fund_name: str) -> tuple[float, str]:
        normalized_symbol = symbol.lower()
        normalized_name = fund_name.lower()

        if normalized_query == normalized_symbol:
            return 200.0, "exact_symbol"
        if normalized_query == normalized_name:
            return 180.0, "exact_name"
        if normalized_name.startswith(normalized_query):
            return 140.0, "prefix_name"
        if normalized_query in normalized_name:
            return 100.0 - (normalized_name.index(normalized_query) * 0.1), "substring_name"
        if normalized_symbol.startswith(normalized_query):
            return 90.0, "prefix_symbol"
        if normalized_query in normalized_symbol:
            return 70.0, "substring_symbol"
        return 0.0, "no_match"
