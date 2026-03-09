from fastapi import APIRouter

from claw_jijin_dogami.models.providers import ProviderStatusResponse
from claw_jijin_dogami.services.providers import get_provider_status

router = APIRouter(prefix="/v1/providers", tags=["providers"])


@router.get("/status", response_model=ProviderStatusResponse)
def get_provider_status_route() -> ProviderStatusResponse:
    return get_provider_status()
