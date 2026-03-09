from datetime import datetime

from pydantic import BaseModel, Field

from .event import EventImpactResponse
from .portfolio import PortfolioAnalyzeResponse


class GeneratedRecommendation(BaseModel):
    action: str
    score: float
    confidence: float = Field(ge=0.0, le=1.0)
    reasons: list[str]
    risk_flags: list[str]


class RecommendationGenerateRequest(BaseModel):
    user_id: str = Field(min_length=1)
    portfolio_id: str = Field(min_length=1)
    cutoff_ts: datetime
    portfolio_analysis: PortfolioAnalyzeResponse
    event_impact: EventImpactResponse | None = None


class RecommendationGenerateResponse(BaseModel):
    user_id: str
    portfolio_id: str
    cutoff_ts: datetime
    recommendation: GeneratedRecommendation
