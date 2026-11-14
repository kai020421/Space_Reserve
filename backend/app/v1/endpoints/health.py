from fastapi import APIRouter

from app.core.responses import success

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    return success({"status": "ok"})
