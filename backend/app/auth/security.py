"""Password hashing (bcrypt) and JWT helpers.  SCRUM-63 / SCRUM-68.

FR-1  : the JWT carries user id and role.
NFR-3 : bcrypt work factor >= 12, tokens signed with a 256-bit secret.
"""
from datetime import datetime, timedelta, timezone
from functools import lru_cache

import bcrypt
import jwt

from app.config import settings
from app.models import User

MIN_SECRET_BYTES = 32  # 256 bits


# ---------------------------------------------------------------- passwords
def hash_password(plain: str) -> str:
    """Return a bcrypt hash (work factor from settings, never below 12)."""
    return bcrypt.hashpw(
        plain.encode("utf-8"), bcrypt.gensalt(rounds=settings.bcrypt_rounds)
    ).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        # e.g. password longer than bcrypt's 72-byte limit, or a malformed hash
        return False


@lru_cache
def dummy_hash() -> str:
    """Checked when the email is unknown, so 'no such user' and 'wrong password'
    take the same time and cannot be told apart by timing."""
    return hash_password("not-a-real-password")


# --------------------------------------------------------------------- JWT
def _secret() -> str:
    key = settings.jwt_secret_key
    if len(key.encode("utf-8")) < MIN_SECRET_BYTES:
        raise RuntimeError(
            "JWT_SECRET_KEY is missing or shorter than 32 bytes (256 bits). "
            "Generate one with:  python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    return key


def create_access_token(user: User) -> tuple[str, datetime]:
    """Return (token, expires_at). Claims: user_id, role, exp, iat (+ erp_id for students)."""
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.access_token_expire_minutes)
    claims: dict = {
        "user_id": user.user_id,
        "role": user.role,
        "iat": now,
        "exp": expires_at,
    }
    if user.role == "STUDENT" and user.erp_id:
        claims["erp_id"] = user.erp_id
    token = jwt.encode(claims, _secret(), algorithm=settings.jwt_algorithm)
    return token, expires_at


def decode_access_token(token: str) -> dict:
    """Verify signature, algorithm and expiry. Raises jwt.PyJWTError if anything is wrong."""
    return jwt.decode(
        token,
        _secret(),
        algorithms=[settings.jwt_algorithm],  # fixed list: blocks alg=none tricks
        options={"require": ["exp", "user_id", "role"]},
    )
