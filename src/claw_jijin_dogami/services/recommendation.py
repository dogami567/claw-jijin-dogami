from claw_jijin_dogami.models.recommendation import (
    GeneratedRecommendation,
    RecommendationGenerateRequest,
    RecommendationGenerateResponse,
)


def generate_recommendation(
    request: RecommendationGenerateRequest,
) -> RecommendationGenerateResponse:
    portfolio = request.portfolio_analysis
    event_impact = request.event_impact
    reasons: list[str] = []
    risk_flags: list[str] = []
    score = 0.0

    if portfolio.summary.unrealized_return_rate > 0.08:
        score += 15
        reasons.append("组合当前仍处于正收益区间。")
    elif portfolio.summary.unrealized_return_rate < -0.05:
        score -= 15
        reasons.append("组合已经出现较明显回撤。")

    for alert in portfolio.alerts:
        risk_flags.append(alert.code)
        if alert.code == "holding_concentration":
            score -= 20
            reasons.append("当前存在单基金集中度风险。")
        elif alert.code == "drawdown_attention":
            score -= 15
            reasons.append("当前亏损幅度已达到需要复核纪律的区间。")

    if event_impact is not None:
        score += event_impact.portfolio_impact_score * 100
        reasons.append(
            f"事件影响分为 {event_impact.portfolio_impact_score:.3f}，"
            "已纳入本次建议综合判断。"
        )
        if event_impact.portfolio_impact_score < -0.1:
            risk_flags.append("negative_event")
        elif event_impact.portfolio_impact_score > 0.1:
            reasons.append("当前事件面对组合形成正向支持。")

    score = max(-100.0, min(100.0, round(score, 2)))

    if "holding_concentration" in risk_flags:
        action = "review"
    elif score <= -25:
        action = "reduce"
    elif score >= 25 and not risk_flags:
        action = "add"
    else:
        action = "hold"

    confidence = 0.55
    if event_impact is not None:
        confidence = min(0.95, round(0.45 + event_impact.confidence * 0.4, 2))
    if risk_flags:
        confidence = min(0.95, round(confidence + 0.1, 2))

    if not reasons:
        reasons.append("当前没有显著正负信号，建议继续观察。")

    return RecommendationGenerateResponse(
        user_id=request.user_id,
        portfolio_id=request.portfolio_id,
        cutoff_ts=request.cutoff_ts,
        recommendation=GeneratedRecommendation(
            action=action,
            score=score,
            confidence=confidence,
            reasons=reasons,
            risk_flags=sorted(set(risk_flags)),
        ),
    )
