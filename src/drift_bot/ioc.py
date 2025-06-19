from collections.abc import AsyncIterable

from dishka import Provider, provide, Scope, from_context, make_async_container

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .core.base import EventRepository, FileStorage

from .infrastructure.database.session import create_session_factory
from .infrastructure.database.repositories import SQLEventRepository

from .infrastructure.s3 import S3Client

from .settings import Settings


class AppProvider(Provider):
    config = from_context(provides=Settings, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_bot(self, config: Settings) -> Bot:
        return Bot(
            token=config.bot.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

    @provide(scope=Scope.APP)
    def get_session_factory(self, config: Settings) -> async_sessionmaker[AsyncSession]:
        return create_session_factory(config.postgres)

    @provide(scope=Scope.REQUEST)
    async def get_session(
            self,
            session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_factory() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    async def get_event_repository(self, session: AsyncSession) -> EventRepository:
        return SQLEventRepository(session)

    @provide(scope=Scope.APP)
    async def get_file_storage(self, config: Settings) -> FileStorage:
        return S3Client(
            endpoint_url=config.s3.S3_URL,
            access_key=config.s3.S3_USER,
            secret_key=config.s3.S3_PASSWORD
        )


settings = Settings()

container = make_async_container(AppProvider(), context={Settings: settings})
