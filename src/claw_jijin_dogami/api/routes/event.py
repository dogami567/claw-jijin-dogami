from fastapi import APIRouter

from claw_jijin_dogami.models.event import EventImpactRequest, EventImpactResponse
from claw_jijin_dogami.services.event import analyze_event_impact

router = APIRouter(prefix="/v1/event", tags=["event"])


@router.post("/impact", response_model=EventImpactResponse)
def analyze_event_impact_route(request: EventImpactRequest) -> EventImpactResponse:
    return analyze_event_impact(request)
