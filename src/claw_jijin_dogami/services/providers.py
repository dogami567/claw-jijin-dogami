from claw_jijin_dogami.models.providers import ProviderStatusResponse
from claw_jijin_dogami.providers import registry as provider_registry


def get_provider_status() -> ProviderStatusResponse:
    registry = provider_registry.get_provider_registry()
    ordered_names = [
        name for name in provider_registry.DEFAULT_PROVIDER_ORDER if name in registry
    ]
    ordered_names.extend(
        name for name in registry if name not in provider_registry.DEFAULT_PROVIDER_ORDER
    )

    return ProviderStatusResponse(
        providers=[registry[name].build_status() for name in ordered_names],
        default_provider_order=list(provider_registry.DEFAULT_PROVIDER_ORDER),
    )
