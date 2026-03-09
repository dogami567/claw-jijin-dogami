from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SyncProvider(str, Enum):
    xalpha = "xalpha"
    akshare = "akshare"
    efinance = "efinance"


class SyncTaskType(str, Enum):
    portfolio_ledger = "portfolio_ledger"
    fund_snapshot = "fund_snapshot"
    fund_disclosure = "fund_disclosure"
    market_event = "market_event"


class SyncPlanRequest(BaseModel):
    user_id: str = Field(min_length=1)
    portfolio_id: str = Field(min_length=1)
    fund_codes: list[str] = Field(default_factory=list)
    as_of: datetime
    include_disclosures: bool = True
    include_market_events: bool = True


class SyncTask(BaseModel):
    provider: SyncProvider
    task_type: SyncTaskType
    target_code: str
    priority: int = Field(ge=1, le=10)
    reason: str


class SyncPlanResponse(BaseModel):
    user_id: str
    portfolio_id: str
    as_of: datetime
    tasks: list[SyncTask]
