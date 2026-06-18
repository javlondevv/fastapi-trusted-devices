# Social posts

## LinkedIn

> Post from your profile. A short personal story + one clear link outperforms a
> feature dump. Add 3–5 hashtags. Reply to comments — LinkedIn rewards early
> engagement too.

```
FastAPI gives you authentication — but not device awareness.

"Log out my other sessions." "We saw a login from a new device." Revoking one
specific device. Every product needs these eventually, and every team rebuilds
them by hand.

So I open-sourced the layer I kept rewriting: fastapi-trusted-devices.

→ bind each session to a device
→ list & revoke devices (or all-but-current)
→ per-device permissions + event hooks
→ auth-agnostic, async SQLAlchemy 2.0, MIT

It's an early alpha (v0.1.0) and I'm genuinely after feedback on the API before
1.0. If you build on FastAPI, I'd love your eyes on it — and a ⭐ helps others
find it.

https://github.com/javlondevv/fastapi-trusted-devices

#Python #FastAPI #OpenSource #WebSecurity #BackendDevelopment
```

## Telegram (@DevFlowJavlon channel)

```
🚀 New open-source release: fastapi-trusted-devices

Trusted-device & session security for FastAPI:
• bind sessions to a device, list & revoke them
• per-device permissions + async event hooks
• auth-agnostic, async SQLAlchemy 2.0, MIT, typed

Early alpha — feedback and contributors very welcome 🙌
A ⭐ helps a lot:
https://github.com/javlondevv/fastapi-trusted-devices
```

## Tweet / X (matches the README "Tweet" button)

```
fastapi-trusted-devices — trusted-device & session security for FastAPI.

Bind sessions to a device, list/revoke them, per-device permissions + hooks.
Auth-agnostic, async SQLAlchemy, MIT. Early alpha — feedback welcome 👇

https://github.com/javlondevv/fastapi-trusted-devices

#FastAPI #Python #security
```

Thread idea (optional follow-up tweets):
1. The gap: FastAPI has auth primitives but no device concept.
2. What you get: list/revoke endpoints + the `require_trusted_device` dependency.
3. The design bet: auth-agnostic + storage behind a protocol — and a call for
   feedback before 1.0.
