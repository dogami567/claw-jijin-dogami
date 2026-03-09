from claw_jijin_dogami.models.integration import (
    ChannelType,
    ClawdbotRenderRequest,
    ClawdbotRenderResponse,
    RenderTarget,
)


def render_for_clawdbot(request: ClawdbotRenderRequest) -> ClawdbotRenderResponse:
    if request.target == RenderTarget.portfolio_analysis:
        return _render_portfolio(request)
    if request.target == RenderTarget.event_impact:
        return _render_event_impact(request)
    if request.target == RenderTarget.job_status:
        return _render_job_status(request)
    raise ValueError(f"unsupported render target: {request.target}")


def _render_portfolio(request: ClawdbotRenderRequest) -> ClawdbotRenderResponse:
    summary = request.payload.get("summary", {})
    recommendation = request.payload.get("recommendation", {})
    alerts = request.payload.get("alerts", [])
    title = "组合分析结果"
    bullets = [
        f"持仓数量：{summary.get('holding_count', 0)}",
        f"浮盈浮亏：{summary.get('unrealized_pnl', 0)}",
        f"建议动作：{recommendation.get('action', 'hold')}",
    ]
    if alerts:
        bullets.append(f"重点风险：{alerts[0].get('message', '请复核组合风险')}")

    if request.channel_type == ChannelType.web:
        bullets.append(f"头号重仓：{summary.get('top_holding_fund_code')}")
        detail_level = "full"
        text = "已生成适合页面展示的详细组合摘要，可继续展开查看结构化指标与风险提示。"
    else:
        detail_level = "compact"
        text = "已压缩为聊天摘要，可在需要时继续查看完整报告。"

    return ClawdbotRenderResponse(
        channel_type=request.channel_type,
        target=request.target,
        title=title,
        summary=text,
        bullets=bullets,
        detail_level=detail_level,
    )


def _render_event_impact(request: ClawdbotRenderRequest) -> ClawdbotRenderResponse:
    impacted_funds = request.payload.get("impacted_funds", [])
    event_summary = request.payload.get("event_summary", "事件影响分析")
    bullets = [
        f"组合影响分：{request.payload.get('portfolio_impact_score', 0)}",
        f"置信度：{request.payload.get('confidence', 0)}",
    ]
    if impacted_funds:
        top = impacted_funds[0]
        bullets.append(f"首要受影响基金：{top.get('fund_name')} ({top.get('direction')})")

    return ClawdbotRenderResponse(
        channel_type=request.channel_type,
        target=request.target,
        title="事件影响结果",
        summary=event_summary,
        bullets=bullets,
        detail_level="full" if request.channel_type == ChannelType.web else "compact",
    )


def _render_job_status(request: ClawdbotRenderRequest) -> ClawdbotRenderResponse:
    title = "任务状态"
    status = request.payload.get("status", "unknown")
    job_id = request.payload.get("job_id", "-")
    kind = request.payload.get("kind", "-")
    bullets = [f"任务编号：{job_id}", f"任务类型：{kind}", f"当前状态：{status}"]

    if request.channel_type == ChannelType.onebot:
        summary = "任务状态已同步，可继续追问结果。"
        detail_level = "compact"
    else:
        summary = "任务状态已同步，页面可继续展示详细阶段信息和结果。"
        detail_level = "full"

    return ClawdbotRenderResponse(
        channel_type=request.channel_type,
        target=request.target,
        title=title,
        summary=summary,
        bullets=bullets,
        detail_level=detail_level,
    )
