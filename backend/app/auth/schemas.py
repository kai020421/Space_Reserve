import re
from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class LoginRequest(BaseModel):
    """
    Student login:
        email + ERP ID + password + STUDENT portal

    Faculty/Admin login:
        email + password + STAFF portal

    Enrollment number is not required during login.
    """

    email: str
    erp_id: str | None = Field(default=None, max_length=32)
    password: str = Field(min_length=1, max_length=128)
    portal: Literal["STUDENT", "STAFF"]

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str) -> str:
        value = value.strip().lower()

        if not _EMAIL_RE.match(value):
            raise ValueError("Email is not a valid email address")

        return value

    @field_validator("erp_id")
    @classmethod
    def clean_erp_id(cls, value: str | None) -> str | None:
        if value is not None:
            return value.strip()

        return None


class LoginUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: str
    role: str


class LoginData(BaseModel):
    token: str
    token_type: str
    expires_at: datetime
    user: LoginUser


class LoginResponse(BaseModel):
    data: LoginData


class MeData(BaseModel):
    user_id: int
    name: str
    email: str
    role: str
    expires_at: datetime
    erp_id: str | None
    program: str | None
    is_ta: bool | None
    department: str | None
    allowed_requester_categories: list[str] | None


class MeResponse(BaseModel):
    data: MeData


class MessageResponse(BaseModel):
    message: str