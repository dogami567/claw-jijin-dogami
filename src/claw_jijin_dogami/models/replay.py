from datetime import datetime

from pydantic import BaseModel, Field


class PublishedSnapshot(BaseModel):
    record_id: str = Field(min_length=1)
    record_type: str = Field(min_length=1)
    target_code: str = Field(min_length=1)
    published_at: datetime
    effective_date: datetime | None = None
    source: str | None = None


class ReplayContextRequest(BaseModel):
    user_id: str = Field(min_length=1)
    portfolio_id: str = Field(min_length=1)
    cutoff_ts: datetime
    snapshots: list[PublishedSnapshot] = Field(default_factory=list)
    events: list[PublishedSnapshot] = Field(default_factory=list)


class ReplayContextResponse(BaseModel):
    user_id: str
    portfolio_id: str
    cutoff_ts: datetime
    eligible_snapshot_count: int
    eligible_event_count: int
    dropped_future_snapshot_count: int
    dropped_future_event_count: int
    latest_snapshot_at: datetime | None = None
    latest_event_at: datetime | None = None
    warnings: list[str]
