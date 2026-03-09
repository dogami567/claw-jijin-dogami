from claw_jijin_dogami.models.event import (
    EventDirection,
    EventImpactRequest,
    EventImpactResponse,
    ImpactedFund,
)


def analyze_event_impact(request: EventImpactRequest) -> EventImpactResponse:
    impacted_funds: list[ImpactedFund] = []
    weighted_scores: list[float] = []

    for exposure in request.exposures:
        raw_score = (
            request.event.sentiment_score
            * request.event.intensity
            * exposure.event_exposure
            * exposure.sensitivity
        )
        impact_score = round(raw_score, 6)
        if impact_score > 0.02:
            direction = EventDirection.positive
        elif impact_score < -0.02:
            direction = EventDirection.negative
        else:
            direction = EventDirection.neutral
        confidence = round(min(1.0, request.event.intensity * exposure.event_exposure), 6)
        impacted_funds.append(
            ImpactedFund(
                fund_code=exposure.fund_code,
                fund_name=exposure.fund_name,
                impact_score=impact_score,
                direction=direction,
                confidence=confidence,
            ),
        )
        weighted_scores.append(impact_score * exposure.portfolio_weight)

    impacted_funds.sort(key=lambda item: abs(item.impact_score), reverse=True)
    portfolio_impact_score = round(sum(weighted_scores), 6)
    confidence = (
        round(sum(item.confidence for item in impacted_funds) / len(impacted_funds), 6)
        if impacted_funds
        else 0.0
    )
    event_summary = f"{request.event.event_type}: {request.event.title}"
    reasoning_summary = (
        "基于事件情绪、事件强度、基金事件暴露和组合权重计算影响分，"
        "结果可作为后续 AI 解释和历史回放评测的结构化输入。"
    )

    return EventImpactResponse(
        user_id=request.user_id,
        portfolio_id=request.portfolio_id,
        cutoff_ts=request.cutoff_ts,
        event_summary=event_summary,
        portfolio_impact_score=portfolio_impact_score,
        confidence=confidence,
        impacted_funds=impacted_funds,
        reasoning_summary=reasoning_summary,
    )
