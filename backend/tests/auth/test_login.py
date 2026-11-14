"""Tests for Student and Faculty/Admin login."""

import jwt
import pytest

from app.config import settings
from tests.conftest import PASSWORD, login_body


def claims_of(token: str) -> dict:

    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )


def assert_error_body(response, status: int):

    assert response.status_code == status, response.text

    body = response.json()

    assert set(body) == {"code", "message"}
    assert body["code"] == status
    assert isinstance(body["message"], str)
    assert body["message"]


# ----------------------------- Student login


async def test_valid_student_login(client, users):

    response = await client.post(
        "/auth/login",
        json=login_body("student"),
    )

    assert response.status_code == 200, response.text

    data = response.json()["data"]

    assert data["token_type"] == "Bearer"
    assert data["expires_at"]

    assert data["user"] == {
        "user_id": users["student"].user_id,
        "name": "Sara Student",
        "email": "student.test@khi.iba.edu.pk",
        "role": "STUDENT",
    }

    claims = claims_of(data["token"])

    assert claims["user_id"] == users["student"].user_id
    assert claims["role"] == "STUDENT"
    assert claims["erp_id"] == "10001"
    assert claims["exp"] > claims["iat"]


async def test_student_login_does_not_require_enrollment_number(client):

    response = await client.post(
        "/auth/login",
        json=login_body("student"),
    )

    assert response.status_code == 200, response.text


async def test_email_is_case_insensitive_and_trimmed(client):

    response = await client.post(
        "/auth/login",
        json=login_body(
            "student",
            email="  Student.Test@KHI.IBA.EDU.PK ",
        ),
    )

    assert response.status_code == 200, response.text


async def test_response_never_contains_password_or_hash(client):

    response = await client.post(
        "/auth/login",
        json=login_body("student"),
    )

    assert response.status_code == 200

    response_text = response.text.lower()

    assert "hashed_password" not in response_text
    assert "$2b$" not in response_text


@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param(
            {"password": "WrongPassword1!"},
            id="wrong-password",
        ),
        pytest.param(
            {"email": "nobody@khi.iba.edu.pk"},
            id="unknown-email",
        ),
        pytest.param(
            {"erp_id": "99999"},
            id="wrong-erp-id",
        ),
    ],
)
async def test_invalid_student_credentials_return_401(
    client,
    overrides,
):

    response = await client.post(
        "/auth/login",
        json=login_body("student", **overrides),
    )

    assert_error_body(response, 401)


async def test_all_student_401_messages_are_identical(client):

    messages = set()

    for overrides in (
        {"password": "WrongPassword1!"},
        {"email": "nobody@khi.iba.edu.pk"},
        {"erp_id": "99999"},
    ):

        response = await client.post(
            "/auth/login",
            json=login_body("student", **overrides),
        )

        assert response.status_code == 401

        messages.add(response.json()["message"])

    assert len(messages) == 1


async def test_student_without_erp_id_returns_400(client):

    body = login_body("student")
    body.pop("erp_id")

    response = await client.post(
        "/auth/login",
        json=body,
    )

    assert_error_body(response, 400)


async def test_student_with_blank_erp_id_returns_400(client):

    response = await client.post(
        "/auth/login",
        json=login_body("student", erp_id="   "),
    )

    assert_error_body(response, 400)


async def test_unenrolled_student_with_wrong_password_returns_401(client):

    response = await client.post(
        "/auth/login",
        json=login_body(
            "unenrolled",
            password="WrongPassword1!",
        ),
    )

    assert_error_body(response, 401)


async def test_unenrolled_student_with_correct_credentials_returns_403(client):

    response = await client.post(
        "/auth/login",
        json=login_body("unenrolled"),
    )

    assert_error_body(response, 403)

    assert "enrolled" in response.json()["message"].lower()


# ----------------------------- Faculty/Admin login


async def test_faculty_login_does_not_require_erp_id(client, users):

    response = await client.post(
        "/auth/login",
        json=login_body("faculty"),
    )

    assert response.status_code == 200, response.text

    data = response.json()["data"]

    assert data["user"]["role"] == "FACULTY"

    claims = claims_of(data["token"])

    assert claims["role"] == "FACULTY"
    assert claims["user_id"] == users["faculty"].user_id
    assert "erp_id" not in claims


async def test_admin_login_uses_staff_portal(client):

    response = await client.post(
        "/auth/login",
        json=login_body("admin"),
    )

    assert response.status_code == 200, response.text

    assert response.json()["data"]["user"]["role"] == "SPACE_ADMIN"

    claims = claims_of(
        response.json()["data"]["token"]
    )

    assert claims["role"] == "SPACE_ADMIN"


async def test_deactivated_staff_account_returns_403(client):

    response = await client.post(
        "/auth/login",
        json=login_body("deactivated"),
    )

    assert_error_body(response, 403)

    assert "deactivated" in response.json()["message"].lower()


async def test_wrong_staff_password_returns_401(client):

    response = await client.post(
        "/auth/login",
        json=login_body(
            "faculty",
            password="WrongPassword1!",
        ),
    )

    assert_error_body(response, 401)


# ----------------------------- Portal/domain checks


@pytest.mark.parametrize(
    "email",
    [
        "someone@gmail.com",
        "someone@iba.edu",
        "student.test@khi.iba.edu.pk.evil.com",
        "student.test@fakekhi.iba.edu.pk",
    ],
)
async def test_non_iba_domain_returns_403(client, email):

    response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": PASSWORD,
            "portal": "STUDENT",
            "erp_id": "10001",
        },
    )

    assert_error_body(response, 403)


async def test_student_email_on_staff_portal_returns_403(client):

    response = await client.post(
        "/auth/login",
        json=login_body("student", portal="STAFF"),
    )

    assert_error_body(response, 403)


async def test_staff_email_on_student_portal_returns_403(client):

    response = await client.post(
        "/auth/login",
        json=login_body(
            "faculty",
            portal="STUDENT",
            erp_id="10001",
        ),
    )

    assert_error_body(response, 403)


async def test_portal_is_required(client):

    body = login_body("student")
    body.pop("portal")

    response = await client.post(
        "/auth/login",
        json=body,
    )

    assert_error_body(response, 400)


async def test_invalid_portal_value_returns_400(client):

    response = await client.post(
        "/auth/login",
        json=login_body(
            "student",
            portal="WHATEVER",
        ),
    )

    assert_error_body(response, 400)


async def test_staff_portal_accepts_faculty_and_admin(client):

    faculty_response = await client.post(
        "/auth/login",
        json=login_body("faculty"),
    )

    admin_response = await client.post(
        "/auth/login",
        json=login_body("admin"),
    )

    assert faculty_response.status_code == 200
    assert admin_response.status_code == 200