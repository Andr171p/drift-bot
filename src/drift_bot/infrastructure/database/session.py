from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from ...settings import PostgresSettings


def create_session_factory(pg_settings: PostgresSettings) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(url=pg_settings.sqlalchemy_url, echo=True)
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False
    )
