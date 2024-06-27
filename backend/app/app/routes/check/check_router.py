from fastapi import APIRouter

checkRouter = APIRouter(prefix="/check")


@checkRouter.get("/health")
async def health_check():
    """
    Endpoint for docker healthcheck
    """
    return {"status": "ok"}
