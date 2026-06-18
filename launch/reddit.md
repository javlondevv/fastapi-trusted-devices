# Reddit posts

Post one subreddit per day, not all at once. **Read each sub's rules first** —
some require a flair, some restrict self-promotion to certain days or ratios.
Lead with the problem, not the repo. Disclose you're the author.

---

## r/FastAPI

**Title:**
```
I built a library to bind FastAPI sessions to trusted devices (list/revoke, alpha — feedback wanted)
```

**Body:**
```
FastAPI handles auth, but there's no built-in concept of *which device* a
session belongs to — so features like "show my active devices," "log out
everywhere," and per-device revocation end up hand-rolled in every project.

I packaged the layer I kept rewriting: fastapi-trusted-devices.

- bind each session to a device_uid
- list/revoke a user's devices (and revoke-all-but-current)
- per-device permissions + async hooks (new device / revoked)
- auth-agnostic (keep your own login/JWT), storage behind a repository
  protocol with an async SQLAlchemy 2.0 adapter included

It's early — v0.1.0, alpha, API may still change — which is exactly why I'm
posting: I want feedback on the API shape before 1.0. MIT, typed, Python
3.10–3.13.

Repo + quickstart: https://github.com/javlondevv/fastapi-trusted-devices

Does the auth-agnostic approach (you pass get_user_id / get_device_uid) feel
right, or would you expect it to own more of the flow?
```

---

## r/Python

**Title:**
```
fastapi-trusted-devices: a device-aware session layer for FastAPI (alpha, MIT, looking for feedback)
```

**Body:**
```
Sharing a small open-source library I've been building.

Problem: web frameworks give you authentication but rarely a notion of trusted
*devices*. "Log out my other sessions," suspicious-login alerts, and
per-device revocation are common product requirements that get reimplemented
over and over.

fastapi-trusted-devices is a focused, auth-agnostic layer for that on FastAPI:
device registry, list/revoke endpoints, per-device permissions, and async
event hooks. Storage sits behind a Protocol (async SQLAlchemy 2.0 adapter
included), so you can swap backends.

Typed (mypy --strict), tested on 3.10–3.13, MIT. It's v0.1.0/alpha and I'm
posting mainly for design feedback before I commit to a 1.0 API.

https://github.com/javlondevv/fastapi-trusted-devices

Happy to answer questions about the design or the threat model.
```

---

## r/webdev

**Title:**
```
Open-source: trusted-device / session management for FastAPI apps (alpha)
```

**Body:**
```
If you've built "manage your logged-in devices" / "log out everywhere" for a
web app, you know it's more fiddly than it looks — tracking devices, scoping
revocation, deciding what counts as suspicious.

I open-sourced the FastAPI version of that work: fastapi-trusted-devices. It
adds a device registry, list/revoke endpoints, per-device permissions, and
hooks for new-device / revoked events, without locking you into a specific auth
library.

Early (v0.1.0, alpha), MIT, Python. Feedback and contributors welcome — there
are a few `good first issue`s open.

https://github.com/javlondevv/fastapi-trusted-devices
```
