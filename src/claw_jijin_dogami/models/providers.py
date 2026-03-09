from pydantic import BaseModel


class ProviderCapabilities(BaseModel):
    live_snapshot: bool = False
    historical_nav: bool = False
    point_in_time_replay: bool = False
    fund_catalog: bool = False
    portfolio_analysis: bool = False


class ProviderStatus(BaseModel):
    name: str
    available: bool
    capabilities: ProviderCapabilities
    detail: str | None = None


class ProviderStatusResponse(BaseModel):
    providers: list[ProviderStatus]
    default_provider_order: list[str]
