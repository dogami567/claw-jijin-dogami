from fastapi import APIRouter

from claw_jijin_dogami.models.replay import ReplayContextRequest, ReplayContextResponse
from claw_jijin_dogami.services.replay import build_replay_context

router = APIRouter(prefix="/v1/replay", tags=["replay"])


@router.post("/context", response_model=ReplayContextResponse)
def build_replay_context_route(request: ReplayContextRequest) -> ReplayContextResponse:
    return build_replay_context(request)
