"""Async event hooks — a typed, testable replacement for Django signals.

Register zero or more async callbacks per event. Emitting awaits each callback
in registration order; a callback raising does not prevent the others from
running, and never breaks the request that triggered the event.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Device

logger = logging.getLogger("fastapi_trusted_devices")

DeviceCallback = Callable[["Device"], Awaitable[None]]


class EventHooks:
    """Registry of async callbacks for device lifecycle events."""

    def __init__(self) -> None:
        self._created: list[DeviceCallback] = []
        self._revoked: list[DeviceCallback] = []

    def on_device_created(self, callback: DeviceCallback) -> DeviceCallback:
        """Register a callback fired when a new device is registered."""
        self._created.append(callback)
        return callback

    def on_device_revoked(self, callback: DeviceCallback) -> DeviceCallback:
        """Register a callback fired when a device is revoked."""
        self._revoked.append(callback)
        return callback

    async def emit_created(self, device: Device) -> None:
        await self._emit(self._created, device)

    async def emit_revoked(self, device: Device) -> None:
        await self._emit(self._revoked, device)

    @staticmethod
    async def _emit(callbacks: list[DeviceCallback], device: Device) -> None:
        for callback in callbacks:
            try:
                await callback(device)
            except Exception:  # hooks must never break the request that fired them
                logger.exception("trusted-devices event hook raised")
