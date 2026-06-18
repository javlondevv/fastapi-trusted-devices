<p align="center">
  <a href="https://github.com/javlondevv/fastapi-trusted-devices">
    <img src="assets/banner.svg" alt="fastapi-trusted-devices" width="100%">
  </a>
</p>

<h1 align="center">fastapi-trusted-devices</h1>

<p align="center">
  Trusted-device management and session security for <b>FastAPI</b> —
  bind every session to a known device, list and revoke devices, and detect
  suspicious activity, without locking into a specific auth library or ORM.
</p>

<p align="center">
  <a href="https://pypi.org/project/fastapi-trusted-devices/"><img src="https://img.shields.io/pypi/v/fastapi-trusted-devices.svg" alt="PyPI"></a>
  <a href="https://pypi.org/project/fastapi-trusted-devices/"><img src="https://img.shields.io/pypi/pyversions/fastapi-trusted-devices.svg" alt="Python versions"></a>
  <a href="https://pypi.org/project/fastapi-trusted-devices/"><img src="https://img.shields.io/pypi/dm/fastapi-trusted-devices.svg?color=blue" alt="PyPI downloads"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT"></a>
  <a href="https://github.com/javlondevv/fastapi-trusted-devices/actions/workflows/ci.yml"><img src="https://github.com/javlondevv/fastapi-trusted-devices/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/badge/code%20style-ruff-261230.svg" alt="Code style: ruff"></a>
  <br>
  <a href="https://github.com/javlondevv/fastapi-trusted-devices/stargazers"><img src="https://img.shields.io/github/stars/javlondevv/fastapi-trusted-devices?style=social" alt="GitHub stars"></a>
  <a href="https://github.com/javlondevv/fastapi-trusted-devices/issues"><img src="https://img.shields.io/github/issues/javlondevv/fastapi-trusted-devices.svg" alt="Open issues"></a>
  <a href="https://github.com/javlondevv/fastapi-trusted-devices/commits/main"><img src="https://img.shields.io/github/last-commit/javlondevv/fastapi-trusted-devices.svg" alt="Last commit"></a>
</p>

<p align="center">
  <b>If this project helps you, please <a href="https://github.com/javlondevv/fastapi-trusted-devices">⭐ star the repo</a> — it really helps others find it.</b>
  &nbsp;·&nbsp;
  <a href="https://twitter.com/intent/tweet?text=fastapi-trusted-devices%20%E2%80%94%20trusted-device%20%26%20session%20security%20for%20FastAPI&url=https://github.com/javlondevv/fastapi-trusted-devices&hashtags=FastAPI,Python,security"><img src="https://img.shields.io/badge/Tweet-share-1DA1F2?logo=twitter&logoColor=white" alt="Tweet"></a>
</p>

---

## Table of contents

- [Status](#status)
- [Why](#why)
- [Install](#install)
- [Quickstart](#quickstart)
- [Endpoints](#endpoints)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Support the project](#support-the-project)
- [License](#license)

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

## Contributing

Contributions are very welcome! See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the
dev setup and checks. Good entry points are the issues labelled
[**good first issue**](https://github.com/javlondevv/fastapi-trusted-devices/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
and [**help wanted**](https://github.com/javlondevv/fastapi-trusted-devices/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22).
Please also read our [Code of Conduct](./CODE_OF_CONDUCT.md).

## Support the project

The simplest way to help is a **⭐ star** — it boosts visibility for everyone.

Embed a live star button on your own site or docs with
[GitHub Buttons](https://buttons.github.io/):

```html
<!-- Place once, before </body> -->
<a class="github-button"
   href="https://github.com/javlondevv/fastapi-trusted-devices"
   data-icon="octicon-star"
   data-size="large"
   data-show-count="true"
   aria-label="Star javlondevv/fastapi-trusted-devices on GitHub">Star</a>
<script async defer src="https://buttons.github.io/buttons.js"></script>
```

## License

MIT — see [`LICENSE`](./LICENSE).
