from claw_jijin_dogami.models.sync import (
    SyncPlanRequest,
    SyncPlanResponse,
    SyncProvider,
    SyncTask,
    SyncTaskType,
)


def build_sync_plan(request: SyncPlanRequest) -> SyncPlanResponse:
    tasks: list[SyncTask] = [
        SyncTask(
            provider=SyncProvider.xalpha,
            task_type=SyncTaskType.portfolio_ledger,
            target_code=request.portfolio_id,
            priority=10,
            reason="组合账本和收益指标以 xalpha 为核心来源，需优先同步。",
        )
    ]

    normalized_codes = sorted({code.strip() for code in request.fund_codes if code.strip()})
    for fund_code in normalized_codes:
        tasks.append(
            SyncTask(
                provider=SyncProvider.akshare,
                task_type=SyncTaskType.fund_snapshot,
                target_code=fund_code,
                priority=9,
                reason="AKShare 作为国内基金公开数据主源，优先拉取净值和排名快照。",
            ),
        )
        tasks.append(
            SyncTask(
                provider=SyncProvider.efinance,
                task_type=SyncTaskType.fund_snapshot,
                target_code=fund_code,
                priority=6,
                reason="efinance 作为免费补充源，用于交叉校验和兜底。",
            ),
        )
        if request.include_disclosures:
            tasks.append(
                SyncTask(
                    provider=SyncProvider.akshare,
                    task_type=SyncTaskType.fund_disclosure,
                    target_code=fund_code,
                    priority=7,
                    reason="基金公开持仓和行业暴露用于消息影响分析与历史回放。",
                ),
            )

    if request.include_market_events:
        tasks.append(
            SyncTask(
                provider=SyncProvider.akshare,
                task_type=SyncTaskType.market_event,
                target_code="market",
                priority=8,
                reason="需要同步宏观、行业和政策事件，为事件影响分析提供输入。",
            ),
        )

    return SyncPlanResponse(
        user_id=request.user_id,
        portfolio_id=request.portfolio_id,
        as_of=request.as_of,
        tasks=tasks,
    )
