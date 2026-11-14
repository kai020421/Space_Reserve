"""Authentication rules for Student and Faculty/Admin portals."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.schemas import LoginRequest
from app.auth.security import dummy_hash, verify_password
from app.errors import AppError
from app.models import User


STUDENT_DOMAIN = "khi.iba.edu.pk"
STAFF_DOMAIN = "iba.edu.pk"

INVALID_CREDENTIALS = "Invalid email, password or ERP ID"

_MEMBERSHIP_CATEGORIES = ("SOCIETY", "CEDIR", "OSA")


def email_domain(email: str) -> str:
    """Extract the exact email domain."""
    return email.rpartition("@")[2].lower()


def authenticate(db: Session, req: LoginRequest) -> User:

    domain = email_domain(req.email)

    # 1. Check whether the email belongs to IBA.
    if domain not in (STUDENT_DOMAIN, STAFF_DOMAIN):
        raise AppError(
            403,
            "Use your IBA email "
            "(@khi.iba.edu.pk for students, "
            "@iba.edu.pk for faculty/admins)",
        )

    is_student_email = domain == STUDENT_DOMAIN
    is_student_portal = req.portal == "STUDENT"

    # 2. Check whether the selected portal matches the email domain.
    if is_student_portal != is_student_email:

        if is_student_portal:
            raise AppError(
                403,
                "Use your @khi.iba.edu.pk student email "
                "on the Student portal",
            )

        raise AppError(
            403,
            "Student emails cannot log in through "
            "the Faculty / Admin portal",
        )

    # 3. ERP ID is compulsory for students only.
    erp_id = (req.erp_id or "").strip()

    if is_student_portal and not erp_id:
        raise AppError(
            400,
            "ERP ID is required for student login",
        )

    # 4. Find the user by email.
    user = db.scalar(
        select(User).where(
            func.lower(User.email) == req.email
        )
    )

    # Always verify a bcrypt hash, even if the email is unknown.
    password_ok = verify_password(
        req.password,
        user.hashed_password if user is not None else dummy_hash(),
    )

    if user is None or not password_ok:
        raise AppError(401, INVALID_CREDENTIALS)

    # 5. Check whether the account role matches the selected portal.
    if is_student_portal and user.role != "STUDENT":
        raise AppError(401, INVALID_CREDENTIALS)

    if not is_student_portal and user.role not in (
        "FACULTY",
        "SPACE_ADMIN",
    ):
        raise AppError(401, INVALID_CREDENTIALS)

    # 6. Verify ERP ID for students.
    if is_student_portal:
        stored_erp_id = (user.erp_id or "").strip()

        if stored_erp_id != erp_id:
            raise AppError(401, INVALID_CREDENTIALS)

    # 7. Check account status.
    if not user.is_active:
        raise AppError(
            403,
            "This account is deactivated",
        )

    # 8. Students must be currently enrolled.
    if user.role == "STUDENT" and not user.is_enrolled:
        raise AppError(
            403,
            "You are not currently enrolled, "
            "so you cannot log in",
        )

    return user


def allowed_requester_categories(user: User) -> list[str] | None:
    """Return booking categories allowed for the user."""

    if user.role == "SPACE_ADMIN":
        return None

    categories: list[str] = []

    if user.role == "STUDENT":
        categories.append("STUDENT")

        if user.is_ta:
            categories.append("FACULTY_TA")

    else:
        categories.append("FACULTY_TA")

    for item in (user.represents or "").split(","):

        item = item.strip().upper()

        if (
            item in _MEMBERSHIP_CATEGORIES
            and item not in categories
        ):
            categories.append(item)

    return categories