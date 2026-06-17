from __future__ import annotations

from collections.abc import AsyncIterator, Callable

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from fastapi_trusted_devices import Base, TrustedDeviceConfig, TrustedDevices


@pytest_asyncio.fixture
async def sessionmaker() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


TdFactory = Callable[[TrustedDeviceConfig | None], TrustedDevices]


@pytest.fixture
def make_td(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> TdFactory:
    """Factory building a facade whose identity comes from request headers."""

    def _make(config: TrustedDeviceConfig | None = None) -> TrustedDevices:
        return TrustedDevices(
            config=config or TrustedDeviceConfig(),
            sessionmaker=sessionmaker,
            get_user_id=lambda request: request.headers["x-user-id"],
            get_device_uid=lambda request: request.headers.get("x-device-uid"),
        )

    return _make
