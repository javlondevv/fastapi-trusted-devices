# Configuration

All behaviour is tuned through `TrustedDeviceConfig`, a frozen Pydantic model
you pass to `TrustedDevices(config=...)`.

```python
from fastapi_trusted_devices import TrustedDeviceConfig

config = TrustedDeviceConfig(
    max_devices_per_user=10,
    update_delay_minutes=0,
    delete_delay_minutes=0,
    trusted_proxy_depth=1,
    concurrent_session_window_seconds=60,
)
```

## Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `max_devices_per_user` | `int \| None` (`≥ 1`) | `None` | Max concurrent devices per user. `None` disables the cap. When a new device would exceed it, the **oldest device is evicted** on registration. |
| `update_delay_minutes` | `int` (`≥ 0`) | `0` | Minimum device age (minutes) before it may be **renamed** / its permissions changed. |
| `delete_delay_minutes` | `int` (`≥ 0`) | `0` | Minimum device age (minutes) before its owner may **revoke** it. (Logout of the current device bypasses this.) |
| `trusted_proxy_depth` | `int` (`≥ 0`) | `0` | How many trusted proxies sit in front of the app, for `X-Forwarded-For` parsing. |
| `concurrent_session_window_seconds` | `int` (`≥ 0`) | `60` | Window (seconds) used by concurrent-session detection (roadmap). |

!!! note "Frozen & strict"
    The model is `frozen=True` and `extra="forbid"` — build a new config rather
    than mutating one, and unknown keys raise a validation error.

## Other constructor options

`TrustedDevices(...)` also accepts:

- `sessionmaker` — your `async_sessionmaker[AsyncSession]`.
- `get_user_id` — `Callable[[Request], str | Awaitable[str]]`.
- `get_device_uid` — `Callable[[Request], str | None | Awaitable[str | None]]`.
- `events` — an optional [`EventHooks`](events.md) registry (one is created if omitted).
- `now` — a `Callable[[], datetime]` clock override, handy in tests.

See the [API Reference](api.md#trusteddevices-facade) for full signatures.
