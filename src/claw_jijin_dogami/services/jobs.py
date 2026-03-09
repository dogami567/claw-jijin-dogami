from datetime import UTC, datetime
from threading import Lock
from uuid import uuid4

from claw_jijin_dogami.models.fund import FundPointInTimeRequest
from claw_jijin_dogami.models.jobs import (
    AsyncJobRecord,
    BacktestJobRequest,
    JobAcceptedResponse,
    JobKind,
    JobStatus,
    ReplayJobRequest,
)
from claw_jijin_dogami.services.fund import get_point_in_time_nav

_jobs: dict[str, AsyncJobRecord] = {}
_lock = Lock()


def enqueue_replay_job(request: ReplayJobRequest) -> JobAcceptedResponse:
    now = datetime.now(UTC)
    job_id = f"replay-{uuid4().hex[:12]}"
    observed_navs, nav_errors = _build_replay_nav_context(request)
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
            "fund_symbols": request.fund_symbols,
            "provider": request.provider,
            "lookback_days": request.lookback_days,
            "observed_navs": observed_navs,
            "nav_errors": nav_errors,
            "evaluation_metrics": {
                "direction_accuracy_20d": 0.0,
                "excess_return_20d": 0.0,
            },
            "note": "Current replay job is a contract-first implementation; real point-in-time execution will replace the stub later.",
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
            "note": "Current backtest job is a contract-first implementation; a real execution engine will replace the stub later.",
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


def _build_replay_nav_context(request: ReplayJobRequest) -> tuple[list[dict], list[dict]]:
    observed_navs: list[dict] = []
    nav_errors: list[dict] = []

    for symbol in request.fund_symbols:
        try:
            response = get_point_in_time_nav(
                FundPointInTimeRequest(
                    symbol=symbol,
                    cutoff_date=request.cutoff_ts.date(),
                    provider=request.provider,
                    lookback_days=request.lookback_days,
                    allow_fallback=True,
                )
            )
            observed_navs.append(
                {
                    "symbol": response.symbol,
                    "provider_used": response.provider_used,
                    "cutoff_date": response.cutoff_date.isoformat(),
                    "point": response.point.model_dump(mode="json"),
                }
            )
        except Exception as exc:
            nav_errors.append({"symbol": symbol, "error": str(exc)})

    return observed_navs, nav_errors
