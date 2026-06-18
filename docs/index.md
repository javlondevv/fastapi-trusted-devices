# FastAPI Trusted Devices

[![PyPI](https://img.shields.io/pypi/v/fastapi-trusted-devices.svg)](https://pypi.org/project/fastapi-trusted-devices/)
[![Python versions](https://img.shields.io/pypi/pyversions/fastapi-trusted-devices.svg)](https://pypi.org/project/fastapi-trusted-devices/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/javlondevv/fastapi-trusted-devices/blob/main/LICENSE)
[![CI](https://github.com/javlondevv/fastapi-trusted-devices/actions/workflows/ci.yml/badge.svg)](https://github.com/javlondevv/fastapi-trusted-devices/actions/workflows/ci.yml)

**Trusted-device management and session security for [FastAPI](https://fastapi.tiangolo.com/).**

FastAPI gives you authentication primitives but no notion of *which device* a
token belongs to. `fastapi-trusted-devices` adds that layer — bind every
authenticated session to a known device, list and revoke devices, and react to
device lifecycle events — **without locking your app into a specific auth library
or ORM**.

!!! warning "Alpha"
    This is `0.1.0` — **alpha**. The core device registry and management
    endpoints are stable enough to use, but the public API may change before
    `1.0`. See the [Roadmap](roadmap.md).

## Features

- 🔐 **Device-bound sessions** — associate each session with a `device_uid`.
- 📋 **List & revoke** — list a user's active devices, revoke one, revoke all-but-current, or log out the current device.
- 🛡️ **Per-device permissions** — control which devices may update or revoke other devices.
- 🧩 **Auth-agnostic** — keep your own login/JWT flow; you pass two callables (`get_user_id`, `get_device_uid`).
- 🗄️ **Storage-abstracted** — everything sits behind a `DeviceRepository` protocol, with an async SQLAlchemy 2.0 adapter included.
- 🪝 **Event hooks** — async callbacks for `on_device_created` and `on_device_revoked`.
- 📈 **Device caps** — optional `max_devices_per_user` with oldest-device eviction.
- ⏱️ **Mutation delays** — optional minimum device age before rename/revoke.
- ⌨️ **Fully typed** — ships `py.typed`, `mypy --strict` clean, tested on Python 3.10–3.13.

## Documentation

<div class="grid cards" markdown>

- :material-download: **[Installation](installation.md)** — install and optional extras.
- :material-rocket-launch: **[Quickstart](quickstart.md)** — a working app in ~30 lines.
- :material-cog: **[Configuration](configuration.md)** — every `TrustedDeviceConfig` field.
- :material-api: **[API Reference](api.md)** — endpoints, schemas, and the facade.
- :material-database: **[Storage & Repository](repository.md)** — the `DeviceRepository` protocol and custom adapters.
- :material-bell: **[Events](events.md)** — device lifecycle hooks.
- :material-alert: **[Exceptions](exceptions.md)** — the error hierarchy and JSON format.

</div>

## Install

```bash
pip install fastapi-trusted-devices
```

## At a glance

```python
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from fastapi_trusted_devices import Base, TrustedDevices, TrustedDeviceConfig

engine = create_async_engine("sqlite+aiosqlite:///./devices.db")
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

td = TrustedDevices(
    config=TrustedDeviceConfig(max_devices_per_user=10),
    sessionmaker=sessionmaker,
    get_user_id=lambda request: request.headers["x-user-id"],
    get_device_uid=lambda request: request.headers.get("x-device-uid"),
)

app = FastAPI()
app.include_router(td.router, prefix="/trusted-devices", tags=["devices"])
td.install_exception_handlers(app)


@app.get("/me", dependencies=[Depends(td.require_trusted_device)])
async def me() -> dict[str, str]:
    return {"ok": "this route requires a recognized device"}
```

Continue to the **[Quickstart](quickstart.md)** for the full runnable example.

---

If this project helps you, please [⭐ star it on GitHub](https://github.com/javlondevv/fastapi-trusted-devices) — it really helps others find it.
