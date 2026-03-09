from datetime import timedelta

from claw_jijin_dogami.models.fund import (
    FundHistoryRequest,
    FundHistoryResponse,
    FundPointInTimeRequest,
    FundPointInTimeResponse,
    FundSnapshotLiveRequest,
    FundSnapshotLiveResponse,
)
from claw_jijin_dogami.providers import registry as provider_registry
from claw_jijin_dogami.providers.base import (
    BaseProviderAdapter,
    ProviderCapabilityError,
    ProviderDataError,
    ProviderUnavailableError,
    UnknownProviderError,
)


def get_live_fund_snapshot(request: FundSnapshotLiveRequest) -> FundSnapshotLiveResponse:
    provider_map = provider_registry.get_provider_registry()
    provider_names = _resolve_provider_names(
        provider_map=provider_map,
        requested_provider=request.provider,
        allow_fallback=request.allow_fallback,
    )

    last_error: Exception | None = None
    symbol = request.symbol.strip()

    for provider_name in provider_names:
        provider = provider_map[provider_name]
        if not provider.is_available():
            last_error = ProviderUnavailableError(provider.name, provider.unavailable_detail())
            continue
        if not provider.capabilities.live_snapshot:
            last_error = ProviderCapabilityError(provider.name, "live_snapshot")
            continue

        try:
            snapshot = provider.fetch_fund_snapshot(symbol)
            return FundSnapshotLiveResponse(
                provider_requested=request.provider,
                provider_used=provider.name,
                snapshot=snapshot,
            )
        except (ProviderDataError, ProviderUnavailableError, ProviderCapabilityError) as exc:
            last_error = exc

    _raise_last_provider_error(last_error)


def get_fund_history(request: FundHistoryRequest) -> FundHistoryResponse:
    provider_map = provider_registry.get_provider_registry()
    provider_names = _resolve_provider_names(
        provider_map=provider_map,
        requested_provider=request.provider,
        allow_fallback=request.allow_fallback,
    )

    last_error: Exception | None = None
    symbol = request.symbol.strip()

    for provider_name in provider_names:
        provider = provider_map[provider_name]
        if not provider.is_available():
            last_error = ProviderUnavailableError(provider.name, provider.unavailable_detail())
            continue
        if not provider.capabilities.historical_nav:
            last_error = ProviderCapabilityError(provider.name, "historical_nav")
            continue

        try:
            points = provider.fetch_fund_history(
                symbol=symbol,
                start_date=request.start_date,
                end_date=request.end_date,
                limit=request.limit,
            )
            return FundHistoryResponse(
                provider_requested=request.provider,
                provider_used=provider.name,
                symbol=symbol,
                point_count=len(points),
                points=points,
            )
        except (ProviderDataError, ProviderUnavailableError, ProviderCapabilityError) as exc:
            last_error = exc

    _raise_last_provider_error(last_error)


def get_point_in_time_nav(request: FundPointInTimeRequest) -> FundPointInTimeResponse:
    history = get_fund_history(
        FundHistoryRequest(
            symbol=request.symbol,
            provider=request.provider,
            start_date=request.cutoff_date - timedelta(days=request.lookback_days),
            end_date=request.cutoff_date,
            limit=min(1000, max(60, request.lookback_days * 2)),
            allow_fallback=request.allow_fallback,
        )
    )

    if not history.points:
        raise ProviderDataError(
            history.provider_used,
            f"no point-in-time nav found for symbol '{request.symbol}' before {request.cutoff_date.isoformat()}",
        )

    return FundPointInTimeResponse(
        provider_requested=request.provider,
        provider_used=history.provider_used,
        symbol=request.symbol.strip(),
        cutoff_date=request.cutoff_date,
        lookback_days=request.lookback_days,
        point=history.points[-1],
    )


def _resolve_provider_names(
    provider_map: dict[str, BaseProviderAdapter],
    requested_provider: str | None,
    allow_fallback: bool,
) -> list[str]:
    if requested_provider is None:
        return list(_ordered_provider_names(provider_map))

    normalized_provider = requested_provider.strip()
    if normalized_provider not in provider_map:
        raise UnknownProviderError(normalized_provider)
    if not allow_fallback:
        return [normalized_provider]

    ordered_names = [normalized_provider]
    ordered_names.extend(
        name for name in _ordered_provider_names(provider_map) if name != normalized_provider
    )
    return ordered_names


def _ordered_provider_names(provider_map: dict[str, BaseProviderAdapter]) -> list[str]:
    ordered = [name for name in provider_registry.DEFAULT_PROVIDER_ORDER if name in provider_map]
    ordered.extend(name for name in provider_map if name not in provider_registry.DEFAULT_PROVIDER_ORDER)
    return ordered


def _raise_last_provider_error(last_error: Exception | None) -> None:
    if last_error is not None:
        raise last_error
    raise ProviderDataError("provider-registry", "no providers configured")
