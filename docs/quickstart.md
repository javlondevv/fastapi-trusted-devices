# Quickstart

This walks through a minimal but complete app: bootstrap the tables, register a
device on login, and protect a route so it only accepts recognized devices.

## 1. Configure the library

```python
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from fastapi_trusted_devices import Base, TrustedDevices, TrustedDeviceConfig

engine = create_async_engine("sqlite+aiosqlite:///./devices.db")
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

td = TrustedDevices(
    config=TrustedDeviceConfig(max_devices_per_user=10),
    sessionmaker=sessionmaker,
    # Tell the library how to identify the caller + their device from a request.
    # Plug in your own auth here (decode a JWT, read a session, etc.).
    get_user_id=lambda request: request.headers["x-user-id"],
    get_device_uid=lambda request: request.headers.get("x-device-uid"),
)
```

`get_user_id` and `get_device_uid` are the only glue you write — they keep the
library **auth-agnostic**. `get_device_uid` may return `None` (e.g. on first
contact) and the request will be rejected for protected routes.

## 2. Mount the router and error handlers

```python
app = FastAPI()
app.include_router(td.router, prefix="/trusted-devices", tags=["devices"])
td.install_exception_handlers(app)


@app.on_event("startup")
async def _startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

In production, prefer Alembic migrations over `create_all` — `Base.metadata`
includes the `trusted_devices` table so it works with autogenerate.

## 3. Register a device at login

After your own login succeeds, register (or look up) the caller's device. The
facade exposes a one-shot helper that opens a session, commits, and returns the
`Device`:

```python
@app.post("/login")
async def login(user_id: str) -> dict[str, str]:
    # ... your real authentication happens here ...
    device = await td.register_device(
        user_id,
        name="My laptop",
        user_agent="Mozilla/5.0 ...",
        ip_address="203.0.113.10",
    )
    # Hand the device_uid back to the client; it sends it on later requests
    # (header, cookie, or embedded in your JWT — your choice).
    return {"device_uid": str(device.device_uid)}
```

## 4. Protect routes

Add the dependency to any route (or whole router) that should require a known
device:

```python
@app.get("/me", dependencies=[Depends(td.require_trusted_device)])
async def me() -> dict[str, str]:
    return {"ok": "this route requires a recognized device"}
```

Need the resolved device inside the handler? Depend on it directly:

```python
from fastapi_trusted_devices import Device

@app.get("/whoami")
async def whoami(device: Device = Depends(td.require_trusted_device)) -> dict:
    return {"device_uid": str(device.device_uid), "name": device.name}
```

## 5. Use the management endpoints

With the router mounted at `/trusted-devices`, your client can now:

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/trusted-devices/` | List the current user's devices |
| `PATCH` | `/trusted-devices/{device_uid}` | Rename / change permissions |
| `DELETE` | `/trusted-devices/{device_uid}` | Revoke a specific device |
| `POST` | `/trusted-devices/logout` | Revoke the current device |
| `POST` | `/trusted-devices/revoke-all` | Revoke every device except the current one |

See the [API Reference](api.md) for request/response schemas, and
[Configuration](configuration.md) for the available knobs.
