from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from fastapi_trusted_devices import (
    DeviceDeletionDisabled,
    DeviceLacksDeletePermission,
    DeviceNotRecognized,
    DeviceUIDMissing,
    EventHooks,
    SQLAlchemyDeviceRepository,
    TrustedDeviceConfig,
    TrustedDeviceService,
)
from fastapi_trusted_devices.models import Device
from fastapi_trusted_devices.schemas import DeviceUpdate


def build_service(
    session: AsyncSession,
    *,
    config: TrustedDeviceConfig | None = None,
    now: datetime | None = None,
    events: EventHooks | None = None,
) -> TrustedDeviceService:
    repo = SQLAlchemyDeviceRepository(session)
    moment = now or datetime(2026, 6, 18, tzinfo=timezone.utc)
    return TrustedDeviceService(
        repo,
        config or TrustedDeviceConfig(),
        events or EventHooks(),
        now=lambda: moment,
    )


async def test_register_and_list(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        service = build_service(session)
        d1 = await service.register_device("u1", name="laptop")
        d2 = await service.register_device("u1", name="phone")
        await session.commit()
        devices = await service.list_devices("u1")
        assert {d.device_uid for d in devices} == {d1.device_uid, d2.device_uid}
        assert await service.list_devices("other") == []


async def test_get_recognized_errors(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        service = build_service(session)
        with pytest.raises(DeviceUIDMissing):
            await service.get_recognized("u1", None)
        with pytest.raises(DeviceNotRecognized):
            await service.get_recognized("u1", uuid.uuid4())


async def test_max_devices_evicts_oldest(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    config = TrustedDeviceConfig(max_devices_per_user=2)
    async with sessionmaker() as session:
        # Stagger creation times so "oldest" is well defined.
        base = datetime(2026, 6, 18, tzinfo=timezone.utc)
        first = build_service(session, config=config, now=base)
        oldest = await first.register_device("u1")
        second = build_service(
            session, config=config, now=base + timedelta(minutes=1)
        )
        await second.register_device("u1")
        third = build_service(
            session, config=config, now=base + timedelta(minutes=2)
        )
        await third.register_device("u1")
        await session.commit()

        remaining = {d.device_uid for d in await third.list_devices("u1")}
        assert len(remaining) == 2
        assert oldest.device_uid not in remaining


async def test_revoke_other_requires_permission(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        service = build_service(session)
        actor = await service.register_device("u1")
        other = await service.register_device("u1")
        await session.commit()

        with pytest.raises(DeviceLacksDeletePermission):
            await service.revoke_device(actor, other.device_uid)

        actor.can_delete_other_devices = True
        await service.revoke_device(actor, other.device_uid)
        await session.commit()
        remaining = {d.device_uid for d in await service.list_devices("u1")}
        assert remaining == {actor.device_uid}


async def test_delete_delay_blocks_then_allows(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    config = TrustedDeviceConfig(delete_delay_minutes=10)
    base = datetime(2026, 6, 18, tzinfo=timezone.utc)
    async with sessionmaker() as session:
        creator = build_service(session, config=config, now=base)
        actor = await creator.register_device("u1")
        actor.can_delete_other_devices = True
        target = await creator.register_device("u1")
        await session.commit()

        too_soon = build_service(
            session, config=config, now=base + timedelta(minutes=5)
        )
        with pytest.raises(DeviceDeletionDisabled):
            await too_soon.revoke_device(actor, target.device_uid)

        later = build_service(
            session, config=config, now=base + timedelta(minutes=15)
        )
        await later.revoke_device(actor, target.device_uid)
        await session.commit()
        assert await later._repo.get("u1", target.device_uid) is None


async def test_logout_bypasses_delete_delay(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    config = TrustedDeviceConfig(delete_delay_minutes=10)
    base = datetime(2026, 6, 18, tzinfo=timezone.utc)
    async with sessionmaker() as session:
        service = build_service(session, config=config, now=base)
        actor = await service.register_device("u1")
        await service.logout(actor)  # immediately, despite the 10-minute delay
        await session.commit()
        assert await service.list_devices("u1") == []


async def test_revoke_all_others_and_events(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    revoked: list[uuid.UUID] = []
    created: list[uuid.UUID] = []
    events = EventHooks()

    @events.on_device_revoked
    async def _on_revoked(device: Device) -> None:
        revoked.append(device.device_uid)

    @events.on_device_created
    async def _on_created(device: Device) -> None:
        created.append(device.device_uid)

    async with sessionmaker() as session:
        service = build_service(session, events=events)
        actor = await service.register_device("u1")
        await service.register_device("u1")
        await service.register_device("u1")
        count = await service.revoke_all_others(actor)
        await session.commit()

        assert count == 2
        assert len(created) == 3
        assert actor.device_uid not in revoked
        remaining = {d.device_uid for d in await service.list_devices("u1")}
        assert remaining == {actor.device_uid}


async def test_update_device_applies_fields(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        service = build_service(session)
        actor = await service.register_device("u1", name="old")
        updated = await service.update_device(
            actor, actor.device_uid, DeviceUpdate(name="new")
        )
        assert updated.name == "new"
