"""SCRUM-70: POST /auth/logout (API Spec 1.1.2)."""
from tests.conftest import auth_header, get_token


async def test_logout_200(client):
    token = await get_token(client, "student")
    resp = await client.post("/auth/logout", headers=auth_header(token))
    assert resp.status_code == 200
    assert set(resp.json()) == {"message"}


async def test_logout_without_token_401(client):
    resp = await client.post("/auth/logout")
    assert resp.status_code == 401
    assert set(resp.json()) == {"code", "message"}


async def test_logout_with_bad_token_401(client):
    assert (await client.post("/auth/logout", headers=auth_header("garbage"))).status_code == 401


async def test_logout_works_for_every_role(client):
    for who in ("student", "faculty", "admin"):
        token = await get_token(client, who)
        assert (await client.post("/auth/logout", headers=auth_header(token))).status_code == 200


async def test_token_still_works_after_logout_documented_limitation(client):
    """Stateless JWT: the server keeps no revocation list, so the token stays valid until
    it expires. The Flutter app must delete it on logout (FR-11). Accepted in the Test
    Strategy. If the team later adds a deny-list, FLIP this test to expect 401."""
    token = await get_token(client, "student")
    await client.post("/auth/logout", headers=auth_header(token))
    assert (await client.get("/auth/me", headers=auth_header(token))).status_code == 200
