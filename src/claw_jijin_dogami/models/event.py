from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class EventDirection(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


class EventPayload(BaseModel):
    event_type: str = Field(min_length=1)
    title: str = Field(min_length=1)
    body: str | None = None
    published_at: datetime
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    intensity: float = Field(ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)


class FundExposureInput(BaseModel):
    fund_code: str = Field(min_length=1)
    fund_name: str = Field(min_length=1)
    portfolio_weight: float = Field(ge=0.0, le=1.0)
    event_exposure: float = Field(ge=0.0, le=1.0)
    sensitivity: float = Field(default=1.0, ge=0.0, le=2.0)


class EventImpactRequest(BaseModel):
    user_id: str = Field(min_length=1)
    portfolio_id: str = Field(min_length=1)
    cutoff_ts: datetime
    event: EventPayload
    exposures: list[FundExposureInput] = Field(default_factory=list)


class ImpactedFund(BaseModel):
    fund_code: str
    fund_name: str
    impact_score: float
    direction: EventDirection
    confidence: float


class EventImpactResponse(BaseModel):
    user_id: str
    portfolio_id: str
    cutoff_ts: datetime
    event_summary: str
    portfolio_impact_score: float
    confidence: float
    impacted_funds: list[ImpactedFund]
    reasoning_summary: str
