from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    info = "info"
    warn = "warn"


class PortfolioRecommendationAction(str, Enum):
    hold = "hold"
    review = "review"
    reduce = "reduce"
    add = "add"


class PortfolioHoldingInput(BaseModel):
    fund_code: str = Field(min_length=1)
    fund_name: str = Field(min_length=1)
    shares: float = Field(ge=0)
    cost_amount: float = Field(ge=0)
    market_value: float = Field(ge=0)
    daily_pnl: float = 0.0
    category: str | None = None


class PortfolioAnalyzeRequest(BaseModel):
    user_id: str = Field(min_length=1)
    portfolio_id: str = Field(min_length=1)
    cutoff_ts: datetime
    holdings: list[PortfolioHoldingInput] = Field(default_factory=list)
    cash_amount: float = Field(default=0.0, ge=0)


class PortfolioSummary(BaseModel):
    total_market_value: float
    total_cost: float
    cash_amount: float
    unrealized_pnl: float
    unrealized_return_rate: float
    daily_pnl: float
    holding_count: int
    top_holding_fund_code: str | None = None
    top_holding_weight: float = 0.0


class PortfolioAlert(BaseModel):
    code: str
    severity: AlertSeverity
    message: str


class PortfolioRecommendationSummary(BaseModel):
    action: PortfolioRecommendationAction
    rationale: str


class PortfolioAnalyzeResponse(BaseModel):
    user_id: str
    portfolio_id: str
    cutoff_ts: datetime
    summary: PortfolioSummary
    alerts: list[PortfolioAlert]
    recommendation: PortfolioRecommendationSummary
