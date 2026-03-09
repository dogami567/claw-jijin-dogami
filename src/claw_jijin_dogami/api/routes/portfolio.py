from fastapi import APIRouter

from claw_jijin_dogami.models.portfolio import PortfolioAnalyzeRequest, PortfolioAnalyzeResponse
from claw_jijin_dogami.services.portfolio import analyze_portfolio

router = APIRouter(prefix="/v1/portfolio", tags=["portfolio"])


@router.post("/analyze", response_model=PortfolioAnalyzeResponse)
def analyze_portfolio_route(request: PortfolioAnalyzeRequest) -> PortfolioAnalyzeResponse:
    return analyze_portfolio(request)
