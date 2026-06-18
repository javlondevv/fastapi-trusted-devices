# Hacker News — Show HN

Post at: https://news.ycombinator.com/submit
Best time: Tue–Thu, ~8–10am US Eastern. URL = the GitHub repo.

> HN rules: don't ask for upvotes anywhere. Post the first comment yourself with
> context. Reply to everything. Expect blunt feedback — engage, don't defend.

---

## Title (≤80 chars)

```
Show HN: FastAPI library to bind sessions to trusted devices (alpha)
```

Alternates:
- `Show HN: Trusted-device management for FastAPI – list and revoke sessions`
- `Show HN: fastapi-trusted-devices – device-aware sessions for FastAPI`

## URL

```
https://github.com/javlondevv/fastapi-trusted-devices
```

## First comment (post immediately after submitting)

```
Author here. FastAPI gives you auth primitives (OAuth2, dependencies, JWT
helpers) but no notion of *which device* a token belongs to — so "log out my
other devices," "this login looks suspicious," and per-device revocation are
things every team re-implements by hand.

fastapi-trusted-devices adds that layer:

- associate each authenticated session with a device_uid
- list a user's active devices and revoke any (or all-but-current)
- per-device permissions
- async hooks for "new device" / "device revoked" (suspicious-login and
  hijack detection are on the 0.2/0.3 roadmap)

Design choices I'd genuinely like feedback on:

- It's auth-agnostic: you keep your own login/JWT flow and pass two callables
  (get_user_id, get_device_uid). I went this way instead of bundling an auth
  system so it drops into existing apps — but it does push device-id plumbing
  onto the caller.
- Storage is behind a DeviceRepository protocol; an async SQLAlchemy 2.0
  adapter ships in the box.

It's v0.1.0 and explicitly alpha — the public API may change before 1.0. It's
MIT, typed (mypy --strict), and tested on Python 3.10–3.13. I'd love criticism
on the API shape and the threat model before I freeze anything.

Repo: https://github.com/javlondevv/fastapi-trusted-devices
```
