"""The public entry point: a mountable, auth-agnostic facade."""

from __future__ import annotations

import inspect
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from datetime import datetime
from typing import TypeVar

from fastapi import Depends, FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .config import TrustedDeviceConfig
from .events import EventHooks
from .exceptions import DeviceNotRecognized, install_exception_handlers
from .models import Device
from .repository import SQLAlchemyDeviceRepository
from .service import TrustedDeviceService, _utcnow

T = TypeVar("T")

#: An identity extractor may be sync or async.
UserIdExtractor = Callable[[Request], str | Awaitable[str]]
DeviceUIDExtractor = Callable[
    [Request], str | None | Awaitable[str | None]
]

#: A FastAPI dependency returning the validated calling device.
DeviceDependency = Callable[..., Awaitable[Device]]


async def _maybe_await(value: T | Awaitable[T]) -> T:
    if inspect.isawaitable(value):
        return await value
    return value


class TrustedDevices:
    """Wires configuration, storage and identity into a FastAPI-ready unit.

    The host application owns authentication: it provides ``get_user_id`` and
    ``get_device_uid`` callables that read the authenticated principal and the
    device claim from the incoming request (e.g. from ``request.state``, a JWT,
    or headers). This keeps the library independent of any auth stack.

    Exposes:
        router: an ``APIRouter`` to mount under any prefix.
        require_trusted_device / current_device: FastAPI dependencies that
            resolve and validate the calling device.
        events: the :class:`EventHooks` registry for lifecycle callbacks.
    """

    def __init__(
        self,
        *,
        config: TrustedDeviceConfig,
        sessionmaker: async_sessionmaker[AsyncSession],
        get_user_id: UserIdExtractor,
        get_device_uid: DeviceUIDExtractor,
        events: EventHooks | None = None,
        now: Callable[[], datetime] = _utcnow,
    ) -> None:
        self._config = config
        self._sessionmaker = sessionmaker
        self._get_user_id = get_user_id
        self._get_device_uid = get_device_uid
        self.events = events or EventHooks()
        self._now = now

        self.require_trusted_device: DeviceDependency = self._build_device_dependency()
        #: Alias of :attr:`require_trusted_device` for readable route signatures.
        self.current_device: DeviceDependency = self.require_trusted_device

        from .router import build_router  # local import avoids an import cycle

        self.router = build_router(self)

    def build_service(self, session: AsyncSession) -> TrustedDeviceService:
        repository = SQLAlchemyDeviceRepository(session)
        return TrustedDeviceService(
            repository, self._config, self.events, now=self._now
        )

    async def session_dependency(self) -> AsyncIterator[AsyncSession]:
        """Request-scoped session; commits on success, rolls back on error."""
        async with self._sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def resolve_user_id(self, request: Request) -> str:
        return await _maybe_await(self._get_user_id(request))

    async def resolve_device_uid(self, request: Request) -> uuid.UUID | None:
        raw = await _maybe_await(self._get_device_uid(request))
        if raw is None:
            return None
        try:
            return uuid.UUID(str(raw))
        except (ValueError, AttributeError, TypeError) as exc:
            raise DeviceNotRecognized("Malformed device identifier.") from exc

    def _build_device_dependency(self) -> DeviceDependency:
        session_dep = self.session_dependency

        async def _require_trusted_device(
            request: Request,
            session: AsyncSession = Depends(session_dep),
        ) -> Device:
            service = self.build_service(session)
            user_id = await self.resolve_user_id(request)
            device_uid = await self.resolve_device_uid(request)
            device = await service.get_recognized(user_id, device_uid)
            client_ip = request.client.host if request.client else None
            await service.touch(device, ip_address=client_ip)
            return device

        return _require_trusted_device

    def install_exception_handlers(self, app: FastAPI) -> None:
        """Register JSON handlers for trusted-device errors on ``app``."""
        install_exception_handlers(app)

    async def register_device(
        self,
        user_id: str,
        *,
        name: str | None = None,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> Device:
        """Open a session, register a device, commit, and return it.

        Call this from your login endpoint after authenticating the user, then
        embed ``device.device_uid`` in the issued token / session.
        """
        async with self._sessionmaker() as session:
            service = self.build_service(session)
            device = await service.register_device(
                user_id, name=name, user_agent=user_agent, ip_address=ip_address
            )
            await session.commit()
            return device
