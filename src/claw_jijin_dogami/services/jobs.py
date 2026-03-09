from datetime import UTC, datetime
from threading import Lock
from uuid import uuid4

from claw_jijin_dogami.models.jobs import (
    AsyncJobRecord,
    BacktestJobRequest,
    JobAcceptedResponse,
    JobKind,
    JobStatus,
    ReplayJobRequest,
)

_jobs: dict[str, AsyncJobRecord] = {}
_lock = Lock()


def enqueue_replay_job(request: ReplayJobRequest) -> JobAcceptedResponse:
    now = datetime.now(UTC)
    job_id = f"replay-{uuid4().hex[:12]}"
    record = AsyncJobRecord(
        job_id=job_id,
        kind=JobKind.replay,
        status=JobStatus.completed,
        user_id=request.user_id,
        portfolio_id=request.portfolio_id,
        created_at=now,
        updated_at=now,
        progress=1.0,
        result={
            "cutoff_ts": request.cutoff_ts.isoformat(),
            "horizons": request.horizons,
            "benchmark_set": request.benchmark_set,
            "evaluation_metrics": {
                "direction_accuracy_20d": 0.0,
                "excess_return_20d": 0.0,
            },
            "note": "当前为接口骨架实现，后续将替换为真实 point-in-time 回放执行器。",
        },
    )
    with _lock:
        _jobs[job_id] = record
    return JobAcceptedResponse(
        job_id=job_id,
        kind=JobKind.replay,
        status=record.status,
        accepted_at=now,
    )


def enqueue_backtest_job(request: BacktestJobRequest) -> JobAcceptedResponse:
    now = datetime.now(UTC)
    job_id = f"backtest-{uuid4().hex[:12]}"
    record = AsyncJobRecord(
        job_id=job_id,
        kind=JobKind.backtest,
        status=JobStatus.completed,
        user_id=request.user_id,
        portfolio_id=request.portfolio_id,
        created_at=now,
        updated_at=now,
        progress=1.0,
        result={
            "strategy_name": request.strategy_name,
            "period": {
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat(),
            },
            "metrics": {
                "annualized_return": 0.0,
                "max_drawdown": 0.0,
                "benchmark_return": 0.0,
            },
            "note": "当前为接口骨架实现，后续将接入真实回测引擎。",
        },
    )
    with _lock:
        _jobs[job_id] = record
    return JobAcceptedResponse(
        job_id=job_id,
        kind=JobKind.backtest,
        status=record.status,
        accepted_at=now,
    )


def get_job(job_id: str) -> AsyncJobRecord | None:
    with _lock:
        return _jobs.get(job_id)
