"""POST /auth/login (SCRUM-63), GET /auth/me (SCRUM-69), POST /auth/logout (SCRUM-70).

Mounted under /api/v1 in app/main.py.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_token_claims
from app.auth.schemas import (
    LoginData,
    LoginRequest,
    LoginResponse,
    LoginUser,
    MeData,
    MeResponse,
    MessageResponse,
)
from app.auth.security import create_access_token
from app.auth.service import allowed_requester_categories, authenticate
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Log in with an IBA email. 200 | 400 | 401 | 403 (API Spec 1.1.1)."""
    user = authenticate(db, payload)
    token, expires_at = create_access_token(user)
    return LoginResponse(
        data=LoginData(
            token=token,
            token_type="Bearer",
            expires_at=expires_at,
            user=LoginUser.model_validate(user),
        )
    )


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user), claims: dict = Depends(get_token_claims)):
    """Profile of the logged-in user (API Spec 1.1.3). Fields that do not apply to the role are null."""
    is_student = user.role == "STUDENT"
    return MeResponse(
        data=MeData(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            role=user.role,
            expires_at=datetime.fromtimestamp(claims["exp"], tz=timezone.utc),
            erp_id=user.erp_id if is_student else None,
            program=user.program if is_student else None,
            is_ta=user.is_ta if is_student else None,
            department=user.department if user.role == "FACULTY" else None,
            allowed_requester_categories=allowed_requester_categories(user),
        )
    )


@router.post("/logout", response_model=MessageResponse)
def logout(_: User = Depends(get_current_user)):
    """Confirm logout (API Spec 1.1.2).

    The server keeps no list of revoked tokens, so this only confirms. The Flutter
    app deletes the token from the device (FR-11, UC-16); a copied token stays
    valid until it expires. The Test Strategy accepts this limitation.
    """
    return MessageResponse(message="Logged out")
