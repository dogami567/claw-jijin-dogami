from claw_jijin_dogami.models.replay import ReplayContextRequest, ReplayContextResponse


def build_replay_context(request: ReplayContextRequest) -> ReplayContextResponse:
    eligible_snapshots = [item for item in request.snapshots if item.published_at <= request.cutoff_ts]
    eligible_events = [item for item in request.events if item.published_at <= request.cutoff_ts]

    warnings: list[str] = []
    if not eligible_snapshots:
        warnings.append("cutoff 时点前没有可用快照，历史回放结果可能失真。")
    if not eligible_events:
        warnings.append("cutoff 时点前没有事件数据，消息归因能力将受限。")

    latest_snapshot_at = max((item.published_at for item in eligible_snapshots), default=None)
    latest_event_at = max((item.published_at for item in eligible_events), default=None)

    return ReplayContextResponse(
        user_id=request.user_id,
        portfolio_id=request.portfolio_id,
        cutoff_ts=request.cutoff_ts,
        eligible_snapshot_count=len(eligible_snapshots),
        eligible_event_count=len(eligible_events),
        dropped_future_snapshot_count=len(request.snapshots) - len(eligible_snapshots),
        dropped_future_event_count=len(request.events) - len(eligible_events),
        latest_snapshot_at=latest_snapshot_at,
        latest_event_at=latest_event_at,
        warnings=warnings,
    )
