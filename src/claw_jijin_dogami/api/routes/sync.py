from fastapi import APIRouter

from claw_jijin_dogami.models.sync import SyncPlanRequest, SyncPlanResponse
from claw_jijin_dogami.services.sync import build_sync_plan

router = APIRouter(prefix="/v1/sync", tags=["sync"])


@router.post("/plan", response_model=SyncPlanResponse)
def build_sync_plan_route(request: SyncPlanRequest) -> SyncPlanResponse:
    return build_sync_plan(request)
