# Events

`fastapi-trusted-devices` emits async lifecycle events you can hook into — log a
new login, send a "new device" email, push to an audit trail, etc.

Hooks live on an `EventHooks` registry. The facade creates one for you and
exposes it as `td.events` (or pass your own via `TrustedDevices(events=...)`).

## Available hooks

| Hook | Fires when | Callback signature |
|---|---|---|
| `on_device_created` | a new device is registered | `async def(device: Device) -> None` |
| `on_device_revoked` | a device is revoked | `async def(device: Device) -> None` |

Both methods double as **decorators** and return the callback, so you can stack
several.

## Usage

```python
from fastapi_trusted_devices import Device

@td.events.on_device_created
async def notify_new_device(device: Device) -> None:
    # e.g. send an email / push notification
    print(f"New device {device.device_uid} for user {device.user_id}")

@td.events.on_device_revoked
async def audit_revocation(device: Device) -> None:
    print(f"Device {device.device_uid} revoked for user {device.user_id}")
```

Callbacks are awaited in registration order whenever the corresponding action
succeeds. Keep them quick (or hand off to a background task / queue) — they run
inside the request that triggered the change.

## Building a registry yourself

```python
from fastapi_trusted_devices import EventHooks, TrustedDevices

events = EventHooks()

@events.on_device_created
async def hook(device): ...

td = TrustedDevices(..., events=events)
```

!!! info "Roadmap"
    Suspicious-login and session-hijack events are planned for `0.2`/`0.3`.
    See the [Roadmap](roadmap.md).
