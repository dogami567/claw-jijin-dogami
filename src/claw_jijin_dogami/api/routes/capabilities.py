from fastapi import APIRouter

from claw_jijin_dogami.models.capabilities import ServiceCapabilities
from claw_jijin_dogami.services.capabilities import get_capabilities

router = APIRouter(prefix="/v1", tags=["capabilities"])


@router.get("/capabilities", response_model=ServiceCapabilities)
def get_service_capabilities() -> ServiceCapabilities:
    return get_capabilities()
