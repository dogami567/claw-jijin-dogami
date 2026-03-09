from claw_jijin_dogami import __version__
from claw_jijin_dogami.models.capabilities import ServiceCapabilities


def get_capabilities() -> ServiceCapabilities:
    return ServiceCapabilities(
        service="claw-jijin-dogami",
        version=__version__,
        supported_channels=["web", "onebot"],
        sync_endpoints=[
            "/v1/providers/status",
            "/v1/fund/search",
            "/v1/fund/snapshot/live",
            "/v1/fund/history",
            "/v1/fund/nav/point-in-time",
            "/v1/portfolio/analyze",
            "/v1/event/impact",
            "/v1/replay/context",
            "/v1/recommendation/generate",
            "/v1/sync/plan",
            "/v1/integrations/clawdbot/render",
        ],
        async_job_kinds=["replay", "backtest"],
        notes=[
            "当前为服务骨架版本，数据源适配与真实回测执行器将后续接入。",
            "建议由 clawdbot 作为多入口调度层统一调用本服务。",
        ],
    )
