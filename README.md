# fastapi-trusted-devices

Trusted-device management and session security for **FastAPI**.

Bind every authenticated session to a known device, list and revoke devices,
and detect suspicious activity — without locking your app into a specific auth
library or ORM.

## Status

`0.1.0` — **Alpha.** Core device registry + management endpoints. The public API
may change before `1.0`. See [`CHANGELOG.md`](./CHANGELOG.md) and the
[roadmap](#roadmap).

## Why

FastAPI gives you authentication primitives but no notion of *which device* a
token belongs to. `fastapi-trusted-devices` adds that layer:

- Associate each session with a `device_uid`.
- List a user's active devices and revoke any of them.
- Per-device permissions (who may update/revoke other devices).
- Hooks for "new device", "device revoked", and (from `0.2`) suspicious-login
  and session-hijack events.

It is **auth-agnostic** (you keep your own login/JWT flow) and **storage
abstracted** behind a `DeviceRepository` protocol (SQLAlchemy 2.0 async adapter
included).

## Install

```bash
pip install fastapi-trusted-devices
# optional extras:
pip install "fastapi-trusted-devices[geo]"   # httpx geolocation backend (0.2+)
pip install "fastapi-trusted-devices[jwt]"   # PyJWT token helpers
```

## Quickstart

```python
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from fastapi_trusted_devices import (
    Base,
    TrustedDevices,
    TrustedDeviceConfig,
)

engine = create_async_engine("sqlite+aiosqlite:///./devices.db")
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

td = TrustedDevices(
    config=TrustedDeviceConfig(max_devices_per_user=10),
    sessionmaker=sessionmaker,
    # tell the library how to identify the caller + their device from a request:
    get_user_id=lambda request: request.headers["x-user-id"],
    get_device_uid=lambda request: request.headers.get("x-device-uid"),
)

app = FastAPI()
app.include_router(td.router, prefix="/trusted-devices", tags=["devices"])
td.install_exception_handlers(app)


@app.on_event("startup")
async def _startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/me", dependencies=[Depends(td.require_trusted_device)])
async def me() -> dict[str, str]:
    return {"ok": "this route requires a recognized device"}
```

### Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | List the current user's devices |
| `PATCH` | `/{device_uid}` | Rename / change permissions of a device |
| `DELETE` | `/{device_uid}` | Revoke a specific device |
| `POST` | `/logout` | Revoke the current device |
| `POST` | `/revoke-all` | Revoke every device except the current one |

## Roadmap

- **0.1** — core registry, CRUD endpoints, dependencies, SQLAlchemy adapter.
- **0.2** — geolocation backend + cache, `X-Forwarded-For` parsing,
  suspicious-login detection.
- **0.3** — concurrent-session/hijack detection, max-device eviction policies,
  rate limiting, PyJWT helpers, docs site.
- **1.0** — API freeze + semver guarantee.

## License

MIT — see [`LICENSE`](./LICENSE).
