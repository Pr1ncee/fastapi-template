from collections.abc import Callable

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.db.db import SQLALCHEMY_DATABASE_URL, get_session
from src.main import app
from src.services.auth_service import AuthService


@pytest.fixture(scope="session")
async def db_session() -> AsyncSession:
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=False,
    )
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=True,
        autocommit=False,
    )

    async with async_session() as session:
        yield session


@pytest.fixture(scope="session")
def override_get_db(db_session: AsyncSession) -> Callable:
    async def _override_get_db():
        yield db_session

    return _override_get_db


@pytest_asyncio.fixture(scope="session")
async def overridden_app_without_cache(override_get_db: Callable) -> FastAPI:
    main_app = app
    app.dependency_overrides[get_session] = override_get_db
    main_app.user_middleware = [
        middleware for middleware in main_app.user_middleware if middleware.cls.__name__ != "CacheMiddleware"
    ]
    return app

@pytest.fixture(scope="session")
async def get_test_token(db_session) -> str:
    test_payload = {}
    return await AuthService.encode_token(payload=test_payload)


@pytest_asyncio.fixture(scope="session")
async def async_test_client() -> AsyncSession:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def async_test_client_authorised(overridden_app_without_cache: FastAPI, get_test_token) -> AsyncSession:
    async with AsyncClient(
        app=overridden_app_without_cache,
        base_url="http://test",
        headers={"Authorization": f"Bearer {get_test_token}"},
    ) as async_client:
        yield async_client
