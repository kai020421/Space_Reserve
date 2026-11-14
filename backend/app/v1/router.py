from fastapi import APIRouter
from app.auth.router import router as auth_router
from app.v1.endpoints import health, debug

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth_router)
api_router.include_router(debug.router)
