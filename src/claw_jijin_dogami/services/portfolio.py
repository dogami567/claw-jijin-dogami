from claw_jijin_dogami.models.portfolio import (
    AlertSeverity,
    PortfolioAlert,
    PortfolioAnalyzeRequest,
    PortfolioAnalyzeResponse,
    PortfolioRecommendationAction,
    PortfolioRecommendationSummary,
    PortfolioSummary,
)


def analyze_portfolio(request: PortfolioAnalyzeRequest) -> PortfolioAnalyzeResponse:
    total_market_value = round(sum(item.market_value for item in request.holdings), 2)
    total_cost = round(sum(item.cost_amount for item in request.holdings), 2)
    daily_pnl = round(sum(item.daily_pnl for item in request.holdings), 2)
    unrealized_pnl = round(total_market_value - total_cost, 2)

    if total_cost > 0:
        unrealized_return_rate = round(unrealized_pnl / total_cost, 6)
    else:
        unrealized_return_rate = 0.0

    top_holding = max(request.holdings, key=lambda item: item.market_value, default=None)
    top_holding_weight = (
        round(top_holding.market_value / total_market_value, 6)
        if top_holding and total_market_value > 0
        else 0.0
    )

    alerts: list[PortfolioAlert] = []
    if top_holding and top_holding_weight >= 0.4:
        alerts.append(
            PortfolioAlert(
                code="holding_concentration",
                severity=AlertSeverity.warn,
                message=(
                    f"{top_holding.fund_name} 仓位占比达到 {top_holding_weight:.1%}，"
                    "需要关注组合集中度风险。"
                ),
            ),
        )
    if unrealized_return_rate <= -0.1:
        alerts.append(
            PortfolioAlert(
                code="drawdown_attention",
                severity=AlertSeverity.warn,
                message="组合浮动亏损超过 10%，建议复核仓位、风格暴露和补仓纪律。",
            ),
        )

    if not request.holdings:
        action = PortfolioRecommendationAction.review
        rationale = "当前组合暂无持仓，请先导入真实交易记录后再生成建议。"
    elif any(alert.code == "holding_concentration" for alert in alerts):
        action = PortfolioRecommendationAction.review
        rationale = "当前更适合先做组合复核，确认集中仓位是否符合你的策略与风险偏好。"
    elif unrealized_return_rate > 0.08:
        action = PortfolioRecommendationAction.hold
        rationale = "组合当前仍处于正收益区间，优先保持纪律，避免频繁交易。"
    elif unrealized_return_rate < -0.05:
        action = PortfolioRecommendationAction.review
        rationale = "组合回撤已扩大，建议结合事件影响与历史评测后再决定是否调仓。"
    else:
        action = PortfolioRecommendationAction.hold
        rationale = "当前组合表现中性，建议继续观察并等待更多基本面或事件信号。"

    return PortfolioAnalyzeResponse(
        user_id=request.user_id,
        portfolio_id=request.portfolio_id,
        cutoff_ts=request.cutoff_ts,
        summary=PortfolioSummary(
            total_market_value=total_market_value,
            total_cost=total_cost,
            cash_amount=round(request.cash_amount, 2),
            unrealized_pnl=unrealized_pnl,
            unrealized_return_rate=unrealized_return_rate,
            daily_pnl=daily_pnl,
            holding_count=len(request.holdings),
            top_holding_fund_code=top_holding.fund_code if top_holding else None,
            top_holding_weight=top_holding_weight,
        ),
        alerts=alerts,
        recommendation=PortfolioRecommendationSummary(action=action, rationale=rationale),
    )
