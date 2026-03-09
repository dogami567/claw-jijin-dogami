from fastapi import APIRouter

from claw_jijin_dogami.models.recommendation import (
    RecommendationGenerateRequest,
    RecommendationGenerateResponse,
)
from claw_jijin_dogami.services.recommendation import generate_recommendation

router = APIRouter(prefix="/v1/recommendation", tags=["recommendation"])


@router.post("/generate", response_model=RecommendationGenerateResponse)
def generate_recommendation_route(
    request: RecommendationGenerateRequest,
) -> RecommendationGenerateResponse:
    return generate_recommendation(request)
