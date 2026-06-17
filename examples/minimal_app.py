"""Runnable minimal example.

    pip install "fastapi-trusted-devices[dev]" uvicorn
    uvicorn examples.minimal_app:app --reload

Identity here is faked via two headers so you can try the endpoints with curl:

    X-User-Id:    the authenticated user's id
    X-Device-Uid: the device's uuid (obtained from POST /login below)

In a real app you would read these from your JWT / session instead.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from fastapi_trusted_devices import Base, TrustedDeviceConfig, TrustedDevices

engine = create_async_engine("sqlite+aiosqlite:///./devices.db")
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

td = TrustedDevices(
    config=TrustedDeviceConfig(max_devices_per_user=5),
    sessionmaker=sessionmaker,
    get_user_id=lambda request: request.headers["x-user-id"],
    get_device_uid=lambda request: request.headers.get("x-device-uid"),
)

app = FastAPI(title="trusted-devices demo")
app.include_router(td.router, prefix="/trusted-devices", tags=["devices"])
td.install_exception_handlers(app)


@app.on_event("startup")
async def _startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.post("/login")
async def login(request: Request) -> dict[str, str]:
    """Pretend-login: registers a device and returns its uid to use as a token."""
    user_id = request.headers["x-user-id"]
    device = await td.register_device(
        user_id,
        name="demo device",
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    return {"device_uid": str(device.device_uid)}
