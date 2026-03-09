from fastapi import APIRouter, HTTPException

from claw_jijin_dogami.models.jobs import (
    AsyncJobRecord,
    BacktestJobRequest,
    JobAcceptedResponse,
    ReplayJobRequest,
)
from claw_jijin_dogami.services.jobs import enqueue_backtest_job, enqueue_replay_job, get_job

router = APIRouter(prefix="/v1/jobs", tags=["jobs"])


@router.post("/replay", response_model=JobAcceptedResponse)
def create_replay_job(request: ReplayJobRequest) -> JobAcceptedResponse:
    return enqueue_replay_job(request)


@router.post("/backtest", response_model=JobAcceptedResponse)
def create_backtest_job(request: BacktestJobRequest) -> JobAcceptedResponse:
    return enqueue_backtest_job(request)


@router.get("/{job_id}", response_model=AsyncJobRecord)
def get_job_status(job_id: str) -> AsyncJobRecord:
    record = get_job(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="job not found")
    return record


@router.get("/{job_id}/result")
def get_job_result(job_id: str) -> dict:
    record = get_job(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="job not found")
    if record.result is None:
        raise HTTPException(status_code=202, detail="job result not ready")
    return {"job_id": record.job_id, "kind": record.kind, "result": record.result}
