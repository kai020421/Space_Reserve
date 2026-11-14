import os

os.environ["JWT_SECRET_KEY"] = (
    "test-secret-key-that-is-definitely-longer-than-32-bytes"
)
os.environ.setdefault("BCRYPT_ROUNDS", "12")

import httpx
import pytest
import pytest_asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.security import hash_password
from app.database import get_db
from app.main import create_app
from app.models import Base, User


BASE_URL = "http://test/api/v1"
PASSWORD = "Test@12345"


USERS = {
    "student": dict(
        name="Sara Student",
        email="student.test@khi.iba.edu.pk",
        role="STUDENT",
        erp_id="10001",
        enrollment_number="EN-10001",
        program="BSCS",
        is_ta=False,
        is_enrolled=True,
    ),

    "unenrolled": dict(
        name="Uzma Unenrolled",
        email="unenrolled.test@khi.iba.edu.pk",
        role="STUDENT",
        erp_id="10002",
        enrollment_number="EN-10002",
        program="BSCS",
        is_ta=False,
        is_enrolled=False,
    ),

    "ta": dict(
        name="Tariq TA",
        email="ta.test@khi.iba.edu.pk",
        role="STUDENT",
        erp_id="10003",
        enrollment_number="EN-10003",
        program="MSCS",
        is_ta=True,
        is_enrolled=True,
        represents="SOCIETY,OSA",
    ),

    "faculty": dict(
        name="Farah Faculty",
        email="faculty.test@iba.edu.pk",
        role="FACULTY",
        department="Computer Science",
    ),

    "admin": dict(
        name="Adil Admin",
        email="admin.test@iba.edu.pk",
        role="SPACE_ADMIN",
    ),

    "deactivated": dict(
        name="Dana Deactivated",
        email="deactivated.test@iba.edu.pk",
        role="FACULTY",
        department="Mathematics",
        is_active=False,
    ),
}


@pytest.fixture(scope="session")
def password_hash() -> str:
    """Create one bcrypt hash and reuse it for test accounts."""
    return hash_password(PASSWORD)


@pytest.fixture
def session_factory(password_hash):

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    factory = sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    with factory() as db:

        for data in USERS.values():
            db.add(
                User(
                    hashed_password=password_hash,
                    **data,
                )
            )

        db.commit()

    yield factory

    engine.dispose()


@pytest.fixture
def db(session_factory):

    with session_factory() as session:
        yield session


@pytest.fixture
def users(db) -> dict[str, User]:

    return {
        key: db.query(User)
        .filter(User.email == data["email"])
        .one()
        for key, data in USERS.items()
    }


@pytest.fixture
def app(session_factory):

    application = create_app()

    def override_get_db():

        with session_factory() as session:
            yield session

    application.dependency_overrides[get_db] = override_get_db

    return application


@pytest_asyncio.fixture
async def client(app):

    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url=BASE_URL,
    ) as c:
        yield c


def login_body(key: str, **overrides) -> dict:
    """
    Generate login data for a seeded account.

    Students send:
        email + ERP ID + password + STUDENT portal.

    Faculty/Admin send:
        email + password + STAFF portal.
    """

    data = USERS[key]

    body = {
        "email": data["email"],
        "password": PASSWORD,
        "portal": (
            "STUDENT"
            if data["role"] == "STUDENT"
            else "STAFF"
        ),
    }

    if data["role"] == "STUDENT":
        body["erp_id"] = data["erp_id"]

    body.update(overrides)

    return body


async def get_token(client: httpx.AsyncClient, key: str) -> str:

    response = await client.post(
        "/auth/login",
        json=login_body(key),
    )

    assert response.status_code == 200, response.text

    return response.json()["data"]["token"]


def auth_header(token: str) -> dict:

    return {
        "Authorization": f"Bearer {token}"
    }