from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/")
def read_root() -> dict[str, str]:
    return {"service": "claw-jijin-dogami", "status": "ok"}


@router.get("/healthz")
def read_healthz() -> dict[str, str]:
    return {"status": "ok"}
