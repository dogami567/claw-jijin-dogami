from claw_jijin_dogami.providers.akshare import AkshareProviderAdapter
from claw_jijin_dogami.providers.base import BaseProviderAdapter
from claw_jijin_dogami.providers.efinance import EfinanceProviderAdapter
from claw_jijin_dogami.providers.xalpha import XalphaProviderAdapter

DEFAULT_PROVIDER_ORDER = ("efinance", "akshare", "xalpha")


def get_provider_registry() -> dict[str, BaseProviderAdapter]:
    providers: tuple[BaseProviderAdapter, ...] = (
        EfinanceProviderAdapter(),
        AkshareProviderAdapter(),
        XalphaProviderAdapter(),
    )
    return {provider.name: provider for provider in providers}
