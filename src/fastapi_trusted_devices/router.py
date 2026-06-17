"""FastAPI router exposing the device-management endpoints."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Device
from .schemas import DeviceOut, DeviceUpdate

if TYPE_CHECKING:
    from .facade import TrustedDevices


def _to_out(device: Device, current_uid: uuid.UUID) -> DeviceOut:
    out = DeviceOut.model_validate(device)
    out.is_current = device.device_uid == current_uid
    return out


def build_router(td: TrustedDevices) -> APIRouter:
    """Construct the device-management router bound to a facade instance."""
    router = APIRouter()
    require_device = td.require_trusted_device
    session_dep = td.session_dependency

    @router.get("", response_model=list[DeviceOut], summary="List my devices")
    async def list_devices(
        actor: Device = Depends(require_device),
        session: AsyncSession = Depends(session_dep),
    ) -> list[DeviceOut]:
        service = td.build_service(session)
        devices = await service.list_devices(actor.user_id)
        return [_to_out(d, actor.device_uid) for d in devices]

    @router.patch(
        "/{device_uid}", response_model=DeviceOut, summary="Update a device"
    )
    async def update_device(
        device_uid: uuid.UUID,
        payload: DeviceUpdate,
        actor: Device = Depends(require_device),
        session: AsyncSession = Depends(session_dep),
    ) -> DeviceOut:
        service = td.build_service(session)
        device = await service.update_device(actor, device_uid, payload)
        return _to_out(device, actor.device_uid)

    @router.delete(
        "/{device_uid}",
        status_code=status.HTTP_204_NO_CONTENT,
        summary="Revoke a device",
    )
    async def revoke_device(
        device_uid: uuid.UUID,
        actor: Device = Depends(require_device),
        session: AsyncSession = Depends(session_dep),
    ) -> None:
        service = td.build_service(session)
        await service.revoke_device(actor, device_uid)

    @router.post(
        "/logout",
        status_code=status.HTTP_204_NO_CONTENT,
        summary="Revoke the current device",
    )
    async def logout(
        actor: Device = Depends(require_device),
        session: AsyncSession = Depends(session_dep),
    ) -> None:
        service = td.build_service(session)
        await service.logout(actor)

    @router.post("/revoke-all", summary="Revoke all devices except this one")
    async def revoke_all(
        actor: Device = Depends(require_device),
        session: AsyncSession = Depends(session_dep),
    ) -> dict[str, int]:
        service = td.build_service(session)
        revoked = await service.revoke_all_others(actor)
        return {"revoked": revoked}

    return router
