---
title: "Why I built fastapi-trusted-devices: device-aware sessions for FastAPI"
published: false
tags: python, fastapi, security, opensource
canonical_url: https://github.com/javlondevv/fastapi-trusted-devices
---

> Publish on [dev.to](https://dev.to/new) (and cross-post to Medium). Flip
> `published: true` when ready. Reply to every comment in the first few hours.

FastAPI gives you excellent authentication primitives — OAuth2 flows,
dependency injection, JWT helpers. But it has **no notion of which *device* a
session belongs to.** And almost every real product eventually needs that:

- "Here are your active sessions — log out the others."
- "We noticed a sign-in from a new device."
- An admin or the user revoking a specific device.

Every team I've worked with re-implements this by hand, slightly differently,
slightly wrong. So I extracted the layer into a small, focused library:
**[fastapi-trusted-devices](https://github.com/javlondevv/fastapi-trusted-devices)**.

> Heads up: it's **v0.1.0, alpha**. It works and it's tested, but the public API
> may change before 1.0. I'm sharing it now precisely to get feedback on the
> design.

## The idea

Bind every authenticated session to a `device_uid`, then give you the operations
you actually need on top of that registry:

- list a user's active devices
- revoke any device — or all devices except the current one
- per-device permissions (who may update/revoke whom)
- async hooks for `on_device_created` / `on_device_revoked`

Two deliberate constraints:

1. **Auth-agnostic.** You keep your own login/JWT flow. The library only needs
   to know how to read the caller and their device from a request — you pass two
   callables.
2. **Storage-abstracted.** Persistence sits behind a `DeviceRepository`
   protocol. An async **SQLAlchemy 2.0** adapter ships in the box; swap in your
   own if you like.

## Quickstart

Install:

```bash
pip install fastapi-trusted-devices
```

Wire it into an app:

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

That `Depends(td.require_trusted_device)` is the payoff: any route guarded by it
now requires a recognized device, not just a valid token.

## The endpoints you get

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | List the current user's devices |
| `PATCH` | `/{device_uid}` | Rename / change permissions of a device |
| `DELETE` | `/{device_uid}` | Revoke a specific device |
| `POST` | `/logout` | Revoke the current device |
| `POST` | `/revoke-all` | Revoke every device except the current one |

## Where it's going

- **0.2** — geolocation backend + caching, `X-Forwarded-For` parsing,
  suspicious-login detection.
- **0.3** — concurrent-session / hijack detection, eviction policies, rate
  limiting, PyJWT helpers, a docs site.
- **1.0** — API freeze + semver guarantee.

It's MIT, typed (`mypy --strict`), and tested on Python 3.10–3.13.

## I'd love your feedback

This is the part where alpha is a feature: the API isn't frozen yet. If you've
built device/session management before, I want to hear where this abstraction
would break for you — especially the auth-agnostic boundary and the threat
model. Open an issue, or grab one of the `good first issue`s.

If it looks useful, a ⭐ genuinely helps other people find it:

```html
<!-- Drop a live star button on your own blog/docs (https://buttons.github.io/) -->
<a class="github-button"
   href="https://github.com/javlondevv/fastapi-trusted-devices"
   data-icon="octicon-star"
   data-size="large"
   data-show-count="true"
   aria-label="Star javlondevv/fastapi-trusted-devices on GitHub">Star</a>
<script async defer src="https://buttons.github.io/buttons.js"></script>
```

👉 **[github.com/javlondevv/fastapi-trusted-devices](https://github.com/javlondevv/fastapi-trusted-devices)** — stars and issues welcome.
