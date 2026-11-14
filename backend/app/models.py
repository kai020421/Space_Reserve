"""SQLAlchemy model mapped to the database team's users table."""
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator


class ApiRoleType(TypeDecorator):
    impl = String(20)
    cache_ok = True

    _to_db = {
        "STUDENT": "student",
        "FACULTY": "faculty",
        "SPACE_ADMIN": "admin",
    }
    _from_db = {
        "student": "STUDENT",
        "ta": "STUDENT",
        "faculty": "FACULTY",
        "admin": "SPACE_ADMIN",
    }

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return self._to_db.get(str(value).upper(), str(value).lower())

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self._from_db.get(value.lower(), value.upper())


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    role: Mapped[str] = mapped_column(ApiRoleType(), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    student_status: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Added by the compatibility migration for AB's login requirements.
    erp_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    enrollment_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    program: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_ta: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    department: Mapped[str | None] = mapped_column(String(120), nullable=True)
    represents: Mapped[str] = mapped_column(Text, nullable=False, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    @property
    def user_id(self):
        return self.id

    @property
    def hashed_password(self):
        return self.password_hash

    @hashed_password.setter
    def hashed_password(self, value):
        self.password_hash = value

    @property
    def is_enrolled(self):
        return self.student_status == "enrolled"

    @is_enrolled.setter
    def is_enrolled(self, value):
        self.student_status = "enrolled" if value else "alumni"
