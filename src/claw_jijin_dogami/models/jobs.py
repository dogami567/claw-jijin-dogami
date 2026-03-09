from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class JobKind(str, Enum):
    replay = "replay"
    backtest = "backtest"


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class ReplayJobRequest(BaseModel):
    user_id: str = Field(min_length=1)
    portfolio_id: str = Field(min_length=1)
    cutoff_ts: datetime
    horizons: list[int] = Field(default_factory=lambda: [5, 20, 60])
    benchmark_set: list[str] = Field(default_factory=lambda: ["buy_hold", "fixed_dca"])
    fund_symbols: list[str] = Field(default_factory=list)
    provider: str | None = None
    lookback_days: int = Field(default=30, ge=1, le=3650)


class BacktestJobRequest(BaseModel):
    user_id: str = Field(min_length=1)
    portfolio_id: str = Field(min_length=1)
    strategy_name: str = Field(min_length=1)
    start_date: date
    end_date: date


class JobAcceptedResponse(BaseModel):
    job_id: str
    kind: JobKind
    status: JobStatus
    accepted_at: datetime


class AsyncJobRecord(BaseModel):
    job_id: str
    kind: JobKind
    status: JobStatus
    user_id: str
    portfolio_id: str
    created_at: datetime
    updated_at: datetime
    progress: float = Field(ge=0.0, le=1.0)
    result: dict[str, Any] | None = None
