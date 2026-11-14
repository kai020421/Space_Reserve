"""get_current_user and require_roles.  SCRUM-68.

  no / bad / expired / tampered token ........ 401
  valid token, role not allowed .............. 403

Use them on any route:

    @router.get("/admin/summary")
    def summary(user: User = Depends(require_roles("SPACE_ADMIN"))): ...

    @router.get("/spaces")
    def spaces(user: User = Depends(get_current_user)): ...

NOTE: SCRUM-12 (Kashaf) is "FastAPI middleware to verify JWT tokens on protected
routes". If hers lands first, keep one version and delete the other.
"""
import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.database import get_db
from app.errors import AppError
from app.models import User

# auto_error=False so we control the status code and the { code, message } body
_bearer = HTTPBearer(auto_error=False)
_WWW = {"WWW-Authenticate": "Bearer"}


def get_token_claims(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    if credentials is None:
        raise AppError(401, "Not authenticated", _WWW)
    try:
        return decode_access_token(credentials.credentials)
    except jwt.PyJWTError:
        # covers: garbage, wrong signature, tampered payload, expired, alg=none, missing claims
        raise AppError(401, "Invalid or expired token", _WWW)


def get_current_user(
    claims: dict = Depends(get_token_claims),
    db: Session = Depends(get_db),
) -> User:
    user = db.get(User, claims["user_id"])
    if user is None or not user.is_active:
        raise AppError(401, "Invalid or expired token", _WWW)
    if user.role != claims["role"]:
        # role changed after the token was issued: make the user log in again
        raise AppError(401, "Token is out of date, please log in again", _WWW)
    return user


def require_roles(*allowed: str):
    """Dependency factory: require_roles("SPACE_ADMIN") or require_roles("FACULTY", "SPACE_ADMIN")."""

    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise AppError(403, "You do not have permission to use this endpoint")
        return user

    return checker
