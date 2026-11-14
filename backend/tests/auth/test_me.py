"""SCRUM-69: GET /auth/me (API Spec 1.1.3)."""
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.config import settings
from tests.conftest import auth_header, get_token


async def me(client, who):
    resp = await client.get("/auth/me", headers=auth_header(await get_token(client, who)))
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


async def test_me_student(client, users):
    d = await me(client, "student")
    assert d["user_id"] == users["student"].user_id
    assert (d["name"], d["email"], d["role"]) == ("Sara Student", "student.test@khi.iba.edu.pk", "STUDENT")
    assert (d["erp_id"], d["program"], d["is_ta"]) == ("10001", "BSCS", False)
    assert d["department"] is None
    assert d["allowed_requester_categories"] == ["STUDENT"]


async def test_me_student_ta_with_memberships(client):
    d = await me(client, "ta")
    assert d["is_ta"] is True
    assert d["allowed_requester_categories"] == ["STUDENT", "FACULTY_TA", "SOCIETY", "OSA"]


async def test_me_faculty_has_department_and_no_student_fields(client):
    d = await me(client, "faculty")
    assert d["role"] == "FACULTY" and d["department"] == "Computer Science"
    assert d["erp_id"] is None and d["program"] is None and d["is_ta"] is None
    assert "FACULTY_TA" in d["allowed_requester_categories"]


async def test_me_admin_categories_null(client):
    d = await me(client, "admin")
    assert d["role"] == "SPACE_ADMIN"
    assert d["allowed_requester_categories"] is None
    assert d["erp_id"] is None and d["department"] is None


async def test_me_has_every_field_even_when_null(client):
    d = await me(client, "admin")
    assert set(d) == {
        "user_id", "name", "email", "role", "expires_at", "erp_id", "program",
        "is_ta", "department", "allowed_requester_categories",
    }


async def test_me_expires_at_matches_token(client):
    login = await client.post("/auth/login", json={"email": "admin.test@iba.edu.pk", "password": "Test@12345"})
    token = login.json()["data"]["token"]
    d = (await client.get("/auth/me", headers=auth_header(token))).json()["data"]
    assert datetime.fromisoformat(d["expires_at"]).timestamp() == pytest.approx(
        jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])["exp"], abs=1
    )


async def test_me_never_exposes_password_hash(client):
    token = await get_token(client, "student")
    text = (await client.get("/auth/me", headers=auth_header(token))).text
    assert "hashed_password" not in text and "$2b$" not in text and "enrollment_number" not in text


async def test_me_without_token_401(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401 and set(resp.json()) == {"code", "message"}


async def test_me_with_expired_token_401(client, users):
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {"user_id": users["student"].user_id, "role": "STUDENT", "exp": now - timedelta(minutes=1)},
        settings.jwt_secret_key, algorithm="HS256",
    )
    assert (await client.get("/auth/me", headers=auth_header(token))).status_code == 401
