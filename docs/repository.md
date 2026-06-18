# Storage & Repository

Persistence sits behind the `DeviceRepository` **protocol**, so you can swap the
storage layer without touching the service. A SQLAlchemy 2.0 async adapter ships
in the box.

## The `DeviceRepository` protocol

```python
from typing import Protocol, runtime_checkable, Sequence
import uuid

@runtime_checkable
class DeviceRepository(Protocol):
    async def list_for_user(self, user_id: str) -> Sequence[Device]: ...
    async def get(self, user_id: str, device_uid: uuid.UUID) -> Device | None: ...
    async def count_for_user(self, user_id: str) -> int: ...
    async def oldest_for_user(self, user_id: str) -> Device | None: ...
    async def add(self, device: Device) -> None: ...
    async def delete(self, device: Device) -> None: ...
```

Any object implementing these six methods is a valid repository.

## Bundled adapter: `SQLAlchemyDeviceRepository`

```python
from fastapi_trusted_devices import SQLAlchemyDeviceRepository

repo = SQLAlchemyDeviceRepository(session)   # session: AsyncSession
```

When you use the `TrustedDevices` facade with a `sessionmaker`, this adapter is
wired up for you per request — you rarely construct it by hand.

## The `Device` model

```python
class Device(Base):
    __tablename__ = "trusted_devices"

    device_uid: uuid.UUID            # primary key, defaults to uuid4
    user_id: str                     # indexed; stored as str to stay PK-agnostic
    name: str | None
    user_agent: str | None
    ip_address: str | None           # IP at registration
    last_ip: str | None              # most recent IP seen
    country: str | None              # populated by the geo backend (roadmap)
    region: str | None
    city: str | None
    created_at: datetime             # tz-aware
    last_seen: datetime              # tz-aware
    can_update_other_devices: bool   # default False
    can_delete_other_devices: bool   # default False
```

`Base` is the package's `DeclarativeBase`. Because `Base.metadata` carries the
`trusted_devices` table, Alembic autogenerate picks it up alongside your own
models.

!!! tip "user_id is a string"
    `user_id` is stored as `str(255)` so the library stays agnostic to your
    primary-key type (int, UUID, ULID…). Convert at the boundary in your
    `get_user_id` callable.

## Writing a custom repository

A minimal in-memory adapter (handy for tests):

```python
import uuid
from typing import Sequence
from fastapi_trusted_devices import Device, DeviceRepository

class InMemoryDeviceRepository:
    def __init__(self) -> None:
        self._devices: dict[uuid.UUID, Device] = {}

    async def list_for_user(self, user_id: str) -> Sequence[Device]:
        return [d for d in self._devices.values() if d.user_id == user_id]

    async def get(self, user_id: str, device_uid: uuid.UUID) -> Device | None:
        d = self._devices.get(device_uid)
        return d if d and d.user_id == user_id else None

    async def count_for_user(self, user_id: str) -> int:
        return sum(1 for d in self._devices.values() if d.user_id == user_id)

    async def oldest_for_user(self, user_id: str) -> Device | None:
        owned = [d for d in self._devices.values() if d.user_id == user_id]
        return min(owned, key=lambda d: d.created_at, default=None)

    async def add(self, device: Device) -> None:
        self._devices[device.device_uid] = device

    async def delete(self, device: Device) -> None:
        self._devices.pop(device.device_uid, None)

# isinstance works thanks to @runtime_checkable:
assert isinstance(InMemoryDeviceRepository(), DeviceRepository)
```

Drive it through `TrustedDeviceService` directly:

```python
from fastapi_trusted_devices import TrustedDeviceService, TrustedDeviceConfig, EventHooks

service = TrustedDeviceService(
    repository=InMemoryDeviceRepository(),
    config=TrustedDeviceConfig(),
    events=EventHooks(),
)
```
