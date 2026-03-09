from __future__ import annotations

from datetime import date

from claw_jijin_dogami.models.fund import FundHistoryPoint, FundLiveSnapshot
from claw_jijin_dogami.models.providers import ProviderCapabilities

from .base import (
    BaseProviderAdapter,
    ProviderDataError,
    first_present,
    pick_field,
    records_from_tabular,
    to_date,
    to_datetime,
    to_float,
)


class EfinanceProviderAdapter(BaseProviderAdapter):
    name = "efinance"
    module_name = "efinance"
    capabilities = ProviderCapabilities(
        live_snapshot=True,
        historical_nav=True,
        fund_catalog=True,
    )

    def fetch_fund_snapshot(self, symbol: str) -> FundLiveSnapshot:
        module = self.require_available()
        fund_namespace = getattr(module, "fund", None)
        if fund_namespace is None:
            raise ProviderDataError(self.name, "missing fund namespace")

        base_info_records = self._get_base_info_records(fund_namespace, symbol)
        history_records = self._get_history_records(fund_namespace, symbol)
        if not base_info_records and not history_records:
            raise ProviderDataError(self.name, f"no data returned for symbol '{symbol}'")

        base_info = base_info_records[0] if base_info_records else {}
        sorted_history_records = self._sort_history_records(history_records)
        latest_history = sorted_history_records[-1] if sorted_history_records else {}

        resolved_symbol = str(
            first_present(
                pick_field(base_info, "基金代码", "代码"),
                pick_field(latest_history, "基金代码", "代码"),
                symbol,
            )
        )
        fund_name = first_present(
            pick_field(base_info, "基金简称", "基金名称", "名称"),
            pick_field(latest_history, "基金简称", "基金名称", "名称"),
        )

        return FundLiveSnapshot(
            symbol=resolved_symbol,
            fund_name=str(fund_name) if fund_name is not None else None,
            provider=self.name,
            as_of=to_datetime(
                first_present(
                    pick_field(latest_history, "日期", "净值日期", "更新时间", "更新日期"),
                    pick_field(base_info, "净值日期", "更新时间", "更新日期"),
                )
            ),
            unit_nav=to_float(
                first_present(
                    pick_field(base_info, "单位净值", "最新净值", "净值", "当前净值"),
                    pick_field(latest_history, "单位净值", "净值", "最新净值"),
                )
            ),
            accumulated_nav=to_float(
                first_present(
                    pick_field(base_info, "累计净值", "累计净值(元)"),
                    pick_field(latest_history, "累计净值", "累计净值(元)"),
                )
            ),
            daily_change_pct=to_float(
                first_present(
                    pick_field(base_info, "日增长率", "涨跌幅", "日涨跌幅"),
                    pick_field(latest_history, "日增长率", "涨跌幅", "日涨跌幅"),
                )
            ),
            raw={
                "base_info": base_info,
                "quote_history": latest_history,
            },
        )

    def fetch_fund_history(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int | None = None,
    ) -> list[FundHistoryPoint]:
        module = self.require_available()
        fund_namespace = getattr(module, "fund", None)
        if fund_namespace is None:
            raise ProviderDataError(self.name, "missing fund namespace")

        history_records = self._sort_history_records(self._get_history_records(fund_namespace, symbol))
        if not history_records:
            raise ProviderDataError(self.name, f"no history returned for symbol '{symbol}'")

        points: list[FundHistoryPoint] = []
        for record in history_records:
            point_date = to_date(pick_field(record, "日期", "净值日期", "date"))
            if point_date is None:
                continue
            if start_date is not None and point_date < start_date:
                continue
            if end_date is not None and point_date > end_date:
                continue

            points.append(
                FundHistoryPoint(
                    date=point_date,
                    unit_nav=to_float(pick_field(record, "单位净值", "净值", "最新净值")),
                    accumulated_nav=to_float(pick_field(record, "累计净值", "累计净值(元)")),
                    daily_change_pct=to_float(pick_field(record, "日增长率", "涨跌幅", "日涨跌幅")),
                    raw=record,
                )
            )

        if limit is not None:
            points = points[-limit:]

        if not points:
            raise ProviderDataError(self.name, f"no history points remained for symbol '{symbol}'")

        return points

    def _get_base_info_records(self, fund_namespace: object, symbol: str) -> list[dict]:
        get_base_info = getattr(fund_namespace, "get_base_info", None)
        if not callable(get_base_info):
            return []

        try:
            return records_from_tabular(get_base_info([symbol]))
        except Exception as exc:
            raise ProviderDataError(self.name, f"failed to load base info: {exc}") from exc

    def _get_history_records(self, fund_namespace: object, symbol: str) -> list[dict]:
        get_quote_history = getattr(fund_namespace, "get_quote_history", None)
        if not callable(get_quote_history):
            return []

        try:
            return records_from_tabular(get_quote_history(symbol))
        except Exception as exc:
            raise ProviderDataError(self.name, f"failed to load history: {exc}") from exc

    def _sort_history_records(self, records: list[dict]) -> list[dict]:
        return sorted(
            records,
            key=lambda record: (
                to_date(pick_field(record, "日期", "净值日期", "date")) is None,
                to_date(pick_field(record, "日期", "净值日期", "date")) or date.min,
            ),
        )
