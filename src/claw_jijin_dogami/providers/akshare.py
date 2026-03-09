from claw_jijin_dogami.models.providers import ProviderCapabilities

from .base import BaseProviderAdapter


class AkshareProviderAdapter(BaseProviderAdapter):
    name = "akshare"
    module_name = "akshare"
    capabilities = ProviderCapabilities(
        fund_catalog=True,
    )

    def status_detail(self) -> str | None:
        if self.is_available():
            return "package available; live snapshot and history adapters are not enabled yet"
        return super().status_detail()
