import logging
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.errors import AppError

logger = logging.getLogger(__name__)

async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.message},
        headers=exc.headers,
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": message},
        headers=exc.headers,
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first = errors[0] if errors else {"loc": (), "msg": "Invalid input"}
    field = ".".join(
        str(part) for part in first.get("loc", ())
        if part not in ("body", "query", "path")
    )
    message = f"{field}: {first['msg']}" if field else first["msg"]
    return JSONResponse(status_code=400, content={"code": 400, "message": message})

async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unexpected server error")
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "Internal server error"},
    )
