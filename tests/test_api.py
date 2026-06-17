from __future__ import annotations

from collections.abc import AsyncIterator

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from fastapi_trusted_devices import TrustedDeviceConfig, TrustedDevices

from .conftest import TdFactory


@pytest_asyncio.fixture
async def client_and_td(
    make_td: TdFactory,
) -> AsyncIterator[tuple[AsyncClient, TrustedDevices]]:
    td = make_td(TrustedDeviceConfig(max_devices_per_user=3))
    app = FastAPI()
    app.include_router(td.router, prefix="/trusted-devices")
    td.install_exception_handlers(app)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://t") as client:
        yield client, td


async def _register(td: TrustedDevices, user_id: str, name: str) -> str:
    device = await td.register_device(user_id, name=name)
    return str(device.device_uid)


async def test_list_marks_current_device(
    client_and_td: tuple[AsyncClient, TrustedDevices],
) -> None:
    client, td = client_and_td
    uid_a = await _register(td, "u1", "a")
    await _register(td, "u1", "b")

    resp = await client.get(
        "/trusted-devices",
        headers={"x-user-id": "u1", "x-device-uid": uid_a},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 2
    current = [d for d in body if d["is_current"]]
    assert len(current) == 1
    assert current[0]["device_uid"] == uid_a


async def test_missing_device_uid_returns_401_code(
    client_and_td: tuple[AsyncClient, TrustedDevices],
) -> None:
    client, td = client_and_td
    await _register(td, "u1", "a")
    resp = await client.get("/trusted-devices", headers={"x-user-id": "u1"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "device_uid_missing"


async def test_unknown_device_returns_401(
    client_and_td: tuple[AsyncClient, TrustedDevices],
) -> None:
    client, _ = client_and_td
    resp = await client.get(
        "/trusted-devices",
        headers={
            "x-user-id": "u1",
            "x-device-uid": "00000000-0000-0000-0000-000000000000",
        },
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "device_not_recognized"


async def test_patch_rename(
    client_and_td: tuple[AsyncClient, TrustedDevices],
) -> None:
    client, td = client_and_td
    uid = await _register(td, "u1", "old")
    resp = await client.patch(
        f"/trusted-devices/{uid}",
        json={"name": "renamed"},
        headers={"x-user-id": "u1", "x-device-uid": uid},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "renamed"


async def test_logout_then_unrecognized(
    client_and_td: tuple[AsyncClient, TrustedDevices],
) -> None:
    client, td = client_and_td
    uid = await _register(td, "u1", "a")
    headers = {"x-user-id": "u1", "x-device-uid": uid}

    resp = await client.post("/trusted-devices/logout", headers=headers)
    assert resp.status_code == 204

    # The device no longer exists, so subsequent calls are rejected.
    resp = await client.get("/trusted-devices", headers=headers)
    assert resp.status_code == 401


async def test_revoke_all_others(
    client_and_td: tuple[AsyncClient, TrustedDevices],
) -> None:
    client, td = client_and_td
    uid = await _register(td, "u1", "a")
    await _register(td, "u1", "b")
    await _register(td, "u1", "c")

    resp = await client.post(
        "/trusted-devices/revoke-all",
        headers={"x-user-id": "u1", "x-device-uid": uid},
    )
    assert resp.status_code == 200
    assert resp.json() == {"revoked": 2}

    resp = await client.get(
        "/trusted-devices",
        headers={"x-user-id": "u1", "x-device-uid": uid},
    )
    assert len(resp.json()) == 1


async def test_delete_specific_device_requires_permission(
    client_and_td: tuple[AsyncClient, TrustedDevices],
) -> None:
    client, td = client_and_td
    uid = await _register(td, "u1", "a")
    other = await _register(td, "u1", "b")

    resp = await client.delete(
        f"/trusted-devices/{other}",
        headers={"x-user-id": "u1", "x-device-uid": uid},
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "device_lacks_delete_permission"
