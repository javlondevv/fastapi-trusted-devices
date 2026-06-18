# API Reference

## HTTP endpoints

The router returned by `td.router` exposes the endpoints below. Mount it at any
prefix; every endpoint requires a recognized device (it depends on
`require_trusted_device` internally).

| Method | Path | Summary | Request body | Response |
|---|---|---|---|---|
| `GET` | `/` | List my devices | — | `list[DeviceOut]` |
| `PATCH` | `/{device_uid}` | Update a device | `DeviceUpdate` | `DeviceOut` |
| `DELETE` | `/{device_uid}` | Revoke a device | — | `204 No Content` |
| `POST` | `/logout` | Revoke the current device | — | `204 No Content` |
| `POST` | `/revoke-all` | Revoke all devices except this one | — | `{"revoked": <int>}` |

### Schemas

=== "DeviceOut"

    ```python
    class DeviceOut(BaseModel):
        device_uid: uuid.UUID
        name: str | None = None
        user_agent: str | None = None
        ip_address: str | None = None
        last_ip: str | None = None
        country: str | None = None
        region: str | None = None
        city: str | None = None
        created_at: datetime
        last_seen: datetime
        can_update_other_devices: bool
        can_delete_other_devices: bool
        is_current: bool = False   # True for the device that issued this request
    ```

=== "DeviceUpdate"

    ```python
    class DeviceUpdate(BaseModel):
        # extra="forbid"
        name: str | None = Field(default=None, max_length=255)
        can_update_other_devices: bool | None = None
        can_delete_other_devices: bool | None = None
    ```

## `TrustedDevices` facade

The main entry point. Construct one and reuse it for the app's lifetime.

```python
TrustedDevices(
    *,
    config: TrustedDeviceConfig,
    sessionmaker: async_sessionmaker[AsyncSession],
    get_user_id: Callable[[Request], str | Awaitable[str]],
    get_device_uid: Callable[[Request], str | None | Awaitable[str | None]],
    events: EventHooks | None = None,
    now: Callable[[], datetime] = <utcnow>,
)
```

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `router` | `APIRouter` | Mount it on your app at any prefix. |
| `require_trusted_device` | dependency | FastAPI dependency resolving to the caller's `Device`; raises if unknown. |
| `current_device` | dependency | Alias of `require_trusted_device`. |
| `events` | `EventHooks` | The lifecycle-callback registry. See [Events](events.md). |

### Methods

```python
def install_exception_handlers(self, app: FastAPI) -> None
```
Register JSON error handlers for all `TrustedDeviceError`s on `app`. See
[Exceptions](exceptions.md).

```python
async def register_device(
    self,
    user_id: str,
    *,
    name: str | None = None,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> Device
```
Open a session, register a device (evicting the oldest if the per-user cap is
hit), commit, and return it. Call this after your own login succeeds.

```python
def build_service(self, session: AsyncSession) -> TrustedDeviceService
async def session_dependency(self) -> AsyncIterator[AsyncSession]
async def resolve_user_id(self, request: Request) -> str
async def resolve_device_uid(self, request: Request) -> uuid.UUID | None
```
Lower-level building blocks — use these when wiring custom routes.

## `TrustedDeviceService`

The framework-free core. The facade builds one per request, but you can drive it
directly (e.g. from a worker or test).

```python
TrustedDeviceService(
    repository: DeviceRepository,
    config: TrustedDeviceConfig,
    events: EventHooks,
    *,
    now: Callable[[], datetime] = <utcnow>,
)
```

| Method | Description |
|---|---|
| `register_device(user_id, *, name=None, user_agent=None, ip_address=None) -> Device` | Register a device; evict oldest if over the cap. |
| `list_devices(user_id) -> Sequence[Device]` | All of a user's devices. |
| `get_recognized(user_id, device_uid) -> Device` | Resolve the caller's device or raise. |
| `touch(device, *, ip_address=None) -> None` | Bump `last_seen` / last IP. |
| `update_device(actor, target_uid, payload: DeviceUpdate) -> Device` | Rename / change permissions, with permission + delay checks. |
| `revoke_device(actor, target_uid) -> Device` | Revoke another device, with permission + delay checks. |
| `logout(actor) -> Device` | Revoke the calling device (bypasses delete delay). |
| `revoke_all_others(actor) -> int` | Revoke every other device; returns the count. |

Storage details (the `DeviceRepository` protocol, the bundled SQLAlchemy adapter,
and the `Device` model) live in [Storage & Repository](repository.md).
