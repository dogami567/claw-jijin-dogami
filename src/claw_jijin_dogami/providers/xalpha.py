from claw_jijin_dogami.models.providers import ProviderCapabilities

from .base import BaseProviderAdapter


class XalphaProviderAdapter(BaseProviderAdapter):
    name = "xalpha"
    module_name = "xalpha"
    capabilities = ProviderCapabilities(
        portfolio_analysis=True,
    )

    def status_detail(self) -> str | None:
        if self.is_available():
            return "package available; portfolio-analysis hooks are reserved for later batches"
        return super().status_detail()
