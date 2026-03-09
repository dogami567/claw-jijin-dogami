from fastapi import APIRouter, HTTPException, status

from claw_jijin_dogami.models.fund import (
    FundHistoryRequest,
    FundHistoryResponse,
    FundSnapshotLiveRequest,
    FundSnapshotLiveResponse,
)
from claw_jijin_dogami.providers.base import (
    ProviderCapabilityError,
    ProviderDataError,
    ProviderUnavailableError,
    UnknownProviderError,
)
from claw_jijin_dogami.services.fund import get_fund_history, get_live_fund_snapshot

router = APIRouter(prefix="/v1/fund", tags=["fund"])


@router.post("/snapshot/live", response_model=FundSnapshotLiveResponse)
def get_live_fund_snapshot_route(
    request: FundSnapshotLiveRequest,
) -> FundSnapshotLiveResponse:
    try:
        return get_live_fund_snapshot(request)
    except UnknownProviderError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProviderUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except ProviderCapabilityError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except ProviderDataError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post("/history", response_model=FundHistoryResponse)
def get_fund_history_route(request: FundHistoryRequest) -> FundHistoryResponse:
    try:
        return get_fund_history(request)
    except UnknownProviderError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProviderUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except ProviderCapabilityError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except ProviderDataError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
