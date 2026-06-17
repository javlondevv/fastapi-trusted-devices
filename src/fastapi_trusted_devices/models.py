"""SQLAlchemy 2.0 (async) ORM model for trusted devices."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for the trusted-devices schema.

    Exposed so host applications can include the table in their own metadata /
    Alembic autogenerate. Use a separate metadata object if you prefer to keep
    this table isolated from the rest of your app.
    """


class Device(Base):
    """A single trusted device bound to a user.

    ``user_id`` is stored as a string so the library stays agnostic to the
    host's primary-key type (int, UUID, etc.) — stringify your user id when
    wiring the identity extractors.
    """

    __tablename__ = "trusted_devices"

    device_uid: Mapped[uuid.UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(String(255), index=True)
    name: Mapped[str | None] = mapped_column(String(255), default=None)
    user_agent: Mapped[str | None] = mapped_column(String(512), default=None)
    ip_address: Mapped[str | None] = mapped_column(String(64), default=None)
    last_ip: Mapped[str | None] = mapped_column(String(64), default=None)
    country: Mapped[str | None] = mapped_column(String(128), default=None)
    region: Mapped[str | None] = mapped_column(String(128), default=None)
    city: Mapped[str | None] = mapped_column(String(128), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    can_update_other_devices: Mapped[bool] = mapped_column(Boolean, default=False)
    can_delete_other_devices: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"<Device {self.device_uid} user={self.user_id!r} name={self.name!r}>"
