"""Persistence abstraction.

:class:`DeviceRepository` is the seam that decouples the service from storage.
A SQLAlchemy 2.0 async adapter ships here; alternative backends (e.g. Redis)
can be added later without touching the service or router.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Device


@runtime_checkable
class DeviceRepository(Protocol):
    """Storage operations the service depends on."""

    async def list_for_user(self, user_id: str) -> Sequence[Device]: ...

    async def get(self, user_id: str, device_uid: uuid.UUID) -> Device | None: ...

    async def count_for_user(self, user_id: str) -> int: ...

    async def oldest_for_user(self, user_id: str) -> Device | None: ...

    async def add(self, device: Device) -> None: ...

    async def delete(self, device: Device) -> None: ...


class SQLAlchemyDeviceRepository:
    """:class:`DeviceRepository` backed by a SQLAlchemy ``AsyncSession``.

    The repository does not commit; transaction boundaries are owned by the
    caller (the request-scoped session dependency), keeping multi-step service
    operations atomic.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_user(self, user_id: str) -> Sequence[Device]:
        result = await self._session.execute(
            select(Device)
            .where(Device.user_id == user_id)
            .order_by(Device.created_at.asc())
        )
        return result.scalars().all()

    async def get(self, user_id: str, device_uid: uuid.UUID) -> Device | None:
        result = await self._session.execute(
            select(Device).where(
                Device.user_id == user_id, Device.device_uid == device_uid
            )
        )
        return result.scalar_one_or_none()

    async def count_for_user(self, user_id: str) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(Device)
            .where(Device.user_id == user_id)
        )
        return int(result.scalar_one())

    async def oldest_for_user(self, user_id: str) -> Device | None:
        result = await self._session.execute(
            select(Device)
            .where(Device.user_id == user_id)
            .order_by(Device.created_at.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def add(self, device: Device) -> None:
        self._session.add(device)
        await self._session.flush()

    async def delete(self, device: Device) -> None:
        await self._session.delete(device)
        await self._session.flush()
