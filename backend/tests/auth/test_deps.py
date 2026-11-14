"""SCRUM-68: JWT helpers, get_current_user and require_roles.

A throw-away router with two protected routes is added to the app, so the dependencies
are tested directly (TC-AUTH-09 / TC-NF-04 style) without waiting for other teams' routes.
"""
import time
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user, require_roles
from app.auth.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.config import settings
from app.models import User
from tests.conftest import auth_header, get_token


@pytest.fixture
def app(app):  # extend the shared app fixture with two protected test routes
    r = APIRouter()

    @r.get("/_test/any")
    def any_user(user: User = Depends(get_current_user)):
        return {"user_id": user.user_id}

    @r.get("/_test/admin")
    def admin_only(user: User = Depends(require_roles("SPACE_ADMIN"))):
        return {"user_id": user.user_id}

    app.include_router(r, prefix="/api/v1")
    return app


def forge(user: User, secret=None, algorithm="HS256", **claim_overrides) -> str:
    now = datetime.now(timezone.utc)
    claims = {"user_id": user.user_id, "role": user.role, "iat": now, "exp": now + timedelta(minutes=5)}
    claims.update(claim_overrides)
    return jwt.encode(claims, secret or settings.jwt_secret_key, algorithm=algorithm)


# ------------------------------------------------------------ password helpers
def test_hash_is_bcrypt_cost_12_and_salted():
    a, b = hash_password("pw"), hash_password("pw")
    assert a != b  # random salt
    assert a.startswith("$2b$") and int(a.split("$")[2]) >= 12


def test_verify_password():
    h = hash_password("secret")
    assert verify_password("secret", h)
    assert not verify_password("Secret", h)
    assert not verify_password("secret", "not-a-bcrypt-hash")
    assert verify_password("x" * 200, h) is False  # over bcrypt's 72-byte limit: must not crash


# ------------------------------------------------------------------ JWT helpers
def test_token_round_trip(users):
    token, expires_at = create_access_token(users["student"])
    claims = decode_access_token(token)
    assert claims["user_id"] == users["student"].user_id
    assert claims["role"] == "STUDENT" and claims["erp_id"] == "10001"
    assert int(expires_at.timestamp()) == claims["exp"]


def test_token_lifetime_matches_setting(users):
    token, expires_at = create_access_token(users["admin"])
    delta = expires_at - datetime.now(timezone.utc)
    assert timedelta(minutes=settings.access_token_expire_minutes - 1) < delta <= timedelta(
        minutes=settings.access_token_expire_minutes
    )


def test_decode_rejects_expired(users):
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(forge(users["student"], exp=datetime.now(timezone.utc) - timedelta(seconds=1)))


def test_decode_rejects_wrong_secret(users):
    with pytest.raises(jwt.InvalidSignatureError):
        decode_access_token(forge(users["student"], secret="another-secret-that-is-also-long-enough-123"))


def test_decode_rejects_alg_none(users):
    token = jwt.encode({"user_id": 1, "role": "SPACE_ADMIN", "exp": time.time() + 300}, key=None, algorithm="none")
    with pytest.raises(jwt.PyJWTError):
        decode_access_token(token)


def test_decode_rejects_missing_claims(users):
    token = jwt.encode({"exp": time.time() + 300}, settings.jwt_secret_key, algorithm="HS256")
    with pytest.raises(jwt.MissingRequiredClaimError):
        decode_access_token(token)


# -------------------------------------------------------------- get_current_user
async def test_no_token_401(client):
    resp = await client.get("/_test/any")
    assert resp.status_code == 401
    assert resp.json() == {"code": 401, "message": "Not authenticated"}


@pytest.mark.parametrize("header", ["Bearer", "Bearer ", "Bearer garbage", "Basic abc", "garbage"])
async def test_malformed_authorization_header_401(client, header):
    resp = await client.get("/_test/any", headers={"Authorization": header})
    assert resp.status_code == 401
    assert set(resp.json()) == {"code", "message"}


async def test_valid_token_200(client, users):
    token = await get_token(client, "student")
    resp = await client.get("/_test/any", headers=auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["user_id"] == users["student"].user_id


async def test_expired_token_401(client, users):
    token = forge(users["student"], exp=datetime.now(timezone.utc) - timedelta(minutes=1))
    resp = await client.get("/_test/any", headers=auth_header(token))
    assert resp.status_code == 401


async def test_tampered_token_401(client):
    token = await get_token(client, "student")
    header, payload, sig = token.split(".")
    resp = await client.get("/_test/any", headers=auth_header(f"{header}.{payload}x.{sig}"))
    assert resp.status_code == 401


async def test_role_escalation_by_forging_claim_401(client, users):
    """Student re-signs a token claiming SPACE_ADMIN with a guessed secret: must fail."""
    token = forge(users["student"], secret="guessed-secret-guessed-secret-guessed", role="SPACE_ADMIN")
    resp = await client.get("/_test/admin", headers=auth_header(token))
    assert resp.status_code == 401


async def test_token_for_deleted_user_401(client, users, db):
    token = await get_token(client, "faculty")
    db.delete(users["faculty"])
    db.commit()
    resp = await client.get("/_test/any", headers=auth_header(token))
    assert resp.status_code == 401


async def test_token_of_user_deactivated_after_login_401(client, users, db):
    token = await get_token(client, "faculty")
    users["faculty"].is_active = False
    db.commit()
    resp = await client.get("/_test/any", headers=auth_header(token))
    assert resp.status_code == 401


async def test_token_with_stale_role_401(client, users, db):
    token = await get_token(client, "faculty")
    users["faculty"].role = "SPACE_ADMIN"
    db.commit()
    resp = await client.get("/_test/any", headers=auth_header(token))
    assert resp.status_code == 401


# ---------------------------------------------------------------- require_roles
async def test_require_roles_allows_matching_role(client):
    token = await get_token(client, "admin")
    assert (await client.get("/_test/admin", headers=auth_header(token))).status_code == 200


@pytest.mark.parametrize("who", ["student", "faculty"])
async def test_require_roles_blocks_other_roles_403(client, who):
    token = await get_token(client, who)
    resp = await client.get("/_test/admin", headers=auth_header(token))
    assert resp.status_code == 403
    assert resp.json()["code"] == 403


async def test_require_roles_without_token_is_401_not_403(client):
    assert (await client.get("/_test/admin")).status_code == 401
