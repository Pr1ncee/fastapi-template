from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.core.config import postgres_config

SQLALCHEMY_DATABASE_URL = postgres_config.ASYNC_URL

Base = declarative_base()

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


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
