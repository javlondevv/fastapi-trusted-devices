"""Framework-free core logic for trusted-device management."""

from __future__ import annotations

import uuid
from collections.abc import Callable, Sequence
from datetime import datetime, timedelta, timezone

from .config import TrustedDeviceConfig
from .events import EventHooks
from .exceptions import (
    DeviceDeletionDisabled,
    DeviceEditingDisabled,
    DeviceLacksDeletePermission,
    DeviceLacksEditPermission,
    DeviceNotRecognized,
    DeviceUIDMissing,
)
from .models import Device
from .repository import DeviceRepository
from .schemas import DeviceUpdate


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TrustedDeviceService:
    """Orchestrates device registration, lookup, mutation and revocation.

    Pure application logic: it talks to a :class:`DeviceRepository` and emits
    :class:`EventHooks`, but knows nothing about HTTP. The ``now`` callable is
    injectable so time-dependent behaviour (delays) is deterministic in tests.
    """

    def __init__(
        self,
        repository: DeviceRepository,
        config: TrustedDeviceConfig,
        events: EventHooks,
        *,
        now: Callable[[], datetime] = _utcnow,
    ) -> None:
        self._repo = repository
        self._config = config
        self._events = events
        self._now = now

    async def register_device(
        self,
        user_id: str,
        *,
        name: str | None = None,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> Device:
        """Register a new device for ``user_id``, evicting the oldest if the
        per-user cap would be exceeded."""
        await self._enforce_device_cap(user_id)
        moment = self._now()
        device = Device(
            device_uid=uuid.uuid4(),
            user_id=user_id,
            name=name,
            user_agent=user_agent,
            ip_address=ip_address,
            last_ip=ip_address,
            created_at=moment,
            last_seen=moment,
        )
        await self._repo.add(device)
        await self._events.emit_created(device)
        return device

    async def list_devices(self, user_id: str) -> Sequence[Device]:
        return await self._repo.list_for_user(user_id)

    async def get_recognized(
        self, user_id: str, device_uid: uuid.UUID | None
    ) -> Device:
        """Return the caller's device, raising if it is missing or unknown."""
        if device_uid is None:
            raise DeviceUIDMissing()
        device = await self._repo.get(user_id, device_uid)
        if device is None:
            raise DeviceNotRecognized()
        return device

    async def touch(self, device: Device, *, ip_address: str | None = None) -> None:
        """Update ``last_seen`` (and last IP) for an active device."""
        device.last_seen = self._now()
        if ip_address is not None:
            device.last_ip = ip_address

    async def update_device(
        self, actor: Device, target_uid: uuid.UUID, payload: DeviceUpdate
    ) -> Device:
        target = await self._resolve_target(
            actor,
            target_uid,
            needs_permission=actor.can_update_other_devices,
            permission_error=DeviceLacksEditPermission,
        )
        self._assert_delay_elapsed(
            target, self._config.update_delay_minutes, DeviceEditingDisabled
        )
        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(target, field, value)
        return target

    async def revoke_device(self, actor: Device, target_uid: uuid.UUID) -> Device:
        target = await self._resolve_target(
            actor,
            target_uid,
            needs_permission=actor.can_delete_other_devices,
            permission_error=DeviceLacksDeletePermission,
        )
        self._assert_delay_elapsed(
            target, self._config.delete_delay_minutes, DeviceDeletionDisabled
        )
        await self._repo.delete(target)
        await self._events.emit_revoked(target)
        return target

    async def logout(self, actor: Device) -> Device:
        """Revoke the calling device itself (logout). Bypasses the delete delay,
        which exists to prevent revoking *other* recently-created devices."""
        await self._repo.delete(actor)
        await self._events.emit_revoked(actor)
        return actor

    async def revoke_all_others(self, actor: Device) -> int:
        """Revoke every device of the user except ``actor``; returns the count."""
        devices = await self._repo.list_for_user(actor.user_id)
        revoked = 0
        for device in devices:
            if device.device_uid == actor.device_uid:
                continue
            await self._repo.delete(device)
            await self._events.emit_revoked(device)
            revoked += 1
        return revoked

    async def _resolve_target(
        self,
        actor: Device,
        target_uid: uuid.UUID,
        *,
        needs_permission: bool,
        permission_error: type[Exception],
    ) -> Device:
        if target_uid == actor.device_uid:
            return actor
        if not needs_permission:
            raise permission_error()
        target = await self._repo.get(actor.user_id, target_uid)
        if target is None:
            raise DeviceNotRecognized()
        return target

    def _assert_delay_elapsed(
        self, device: Device, delay_minutes: int, error: type[Exception]
    ) -> None:
        if delay_minutes <= 0:
            return
        if self._now() - device.created_at < timedelta(minutes=delay_minutes):
            raise error()

    async def _enforce_device_cap(self, user_id: str) -> None:
        cap = self._config.max_devices_per_user
        if cap is None:
            return
        while await self._repo.count_for_user(user_id) >= cap:
            oldest = await self._repo.oldest_for_user(user_id)
            if oldest is None:
                return
            await self._repo.delete(oldest)
            await self._events.emit_revoked(oldest)
