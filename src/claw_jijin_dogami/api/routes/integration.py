from fastapi import APIRouter

from claw_jijin_dogami.models.integration import ClawdbotRenderRequest, ClawdbotRenderResponse
from claw_jijin_dogami.services.integration import render_for_clawdbot

router = APIRouter(prefix="/v1/integrations/clawdbot", tags=["integration"])


@router.post("/render", response_model=ClawdbotRenderResponse)
def render_for_clawdbot_route(request: ClawdbotRenderRequest) -> ClawdbotRenderResponse:
    return render_for_clawdbot(request)
