from pydantic import BaseModel


class ServiceCapabilities(BaseModel):
    service: str
    version: str
    supported_channels: list[str]
    sync_endpoints: list[str]
    async_job_kinds: list[str]
    notes: list[str]
