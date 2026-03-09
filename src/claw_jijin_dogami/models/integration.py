from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ChannelType(str, Enum):
    web = "web"
    onebot = "onebot"
    other = "other"


class RenderTarget(str, Enum):
    portfolio_analysis = "portfolio_analysis"
    event_impact = "event_impact"
    job_status = "job_status"


class ClawdbotRenderRequest(BaseModel):
    channel_type: ChannelType
    target: RenderTarget
    payload: dict[str, Any] = Field(default_factory=dict)


class ClawdbotRenderResponse(BaseModel):
    channel_type: ChannelType
    target: RenderTarget
    title: str
    summary: str
    bullets: list[str]
    detail_level: str
