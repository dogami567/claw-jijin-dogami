from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FundLiveSnapshot(BaseModel):
    symbol: str
    fund_name: str | None = None
    provider: str
    as_of: datetime | None = None
    unit_nav: float | None = None
    accumulated_nav: float | None = None
    daily_change_pct: float | None = None
    currency: str = "CNY"
    raw: dict[str, Any] = Field(default_factory=dict)


class FundSnapshotLiveRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    symbol: str = Field(min_length=1)
    provider: str | None = None
    allow_fallback: bool = True


class FundSnapshotLiveResponse(BaseModel):
    provider_requested: str | None = None
    provider_used: str
    snapshot: FundLiveSnapshot


class FundHistoryPoint(BaseModel):
    date: date
    unit_nav: float | None = None
    accumulated_nav: float | None = None
    daily_change_pct: float | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class FundHistoryRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    symbol: str = Field(min_length=1)
    provider: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    limit: int = Field(default=60, ge=1, le=1000)
    allow_fallback: bool = True

    @model_validator(mode="after")
    def validate_dates(self) -> "FundHistoryRequest":
        if self.start_date is not None and self.end_date is not None and self.start_date > self.end_date:
            raise ValueError("start_date must be less than or equal to end_date")
        return self


class FundHistoryResponse(BaseModel):
    provider_requested: str | None = None
    provider_used: str
    symbol: str
    point_count: int
    points: list[FundHistoryPoint]


class FundPointInTimeRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    symbol: str = Field(min_length=1)
    cutoff_date: date
    provider: str | None = None
    lookback_days: int = Field(default=30, ge=1, le=3650)
    allow_fallback: bool = True


class FundPointInTimeResponse(BaseModel):
    provider_requested: str | None = None
    provider_used: str
    symbol: str
    cutoff_date: date
    lookback_days: int
    point: FundHistoryPoint


class FundSearchCandidate(BaseModel):
    symbol: str
    fund_name: str
    fund_type: str | None = None
    provider: str
    score: float
    match_reason: str
    raw: dict[str, Any] = Field(default_factory=dict)


class FundSearchRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(min_length=1)
    provider: str | None = None
    limit: int = Field(default=10, ge=1, le=50)
    allow_fallback: bool = True


class FundSearchResponse(BaseModel):
    provider_requested: str | None = None
    provider_used: str
    query: str
    candidate_count: int
    candidates: list[FundSearchCandidate]
