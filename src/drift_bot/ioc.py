from collections.abc import AsyncIterable

from dishka import Provider, provide, Scope, from_context, make_async_container

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .core.domain import User, Referral, Championship, Stage
from .core.services import CRUDService, ReferralService
from .core.base import (
    FileStorage,
    CRUDRepository,
    ChampionshipRepository,
    StageRepository,
)

from .infrastructure.database.session import create_session_factory
from .infrastructure.database.repositories import (
    SQLUserRepository,
    SQLStageRepository,
    SQLReferralRepository,
    SQLChampionshipRepository
)

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
    def get_championship_repository(self, session: AsyncSession) -> ChampionshipRepository:
        return SQLChampionshipRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_stage_repository(self, session: AsyncSession) -> StageRepository:
        return SQLStageRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_user_repository(self, session: AsyncSession) -> CRUDRepository[User]:
        return SQLUserRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_referral_repository(self, session: AsyncSession) -> CRUDRepository[Referral]:
        return SQLReferralRepository(session)

    @provide(scope=Scope.APP)
    def get_file_storage(self, config: Settings) -> FileStorage:
        return S3Client(
            endpoint_url=config.s3.S3_URL,
            access_key=config.s3.S3_USER,
            secret_key=config.s3.S3_PASSWORD
        )

    @provide(scope=Scope.REQUEST)
    def get_referral_service(self, referral_repository: CRUDRepository[Referral]) -> ReferralService:
        return ReferralService(referral_repository)

    @provide(scope=Scope.REQUEST)
    def get_championship_crud_service(
            self,
            championship_repository: ChampionshipRepository,
            file_storage: FileStorage
    ) -> CRUDService[Championship]:
        return CRUDService[Championship](
            crud_repository=championship_repository,
            file_storage=file_storage
        )

    @provide(scope=Scope.REQUEST)
    def get_stage_crud_service(
            self,
            stage_repository: StageRepository,
            file_storage: FileStorage
    ) -> CRUDService[Stage]:
        return CRUDService[Stage](
            crud_repository=stage_repository,
            file_storage=file_storage
        )


settings = Settings()

container = make_async_container(AppProvider(), context={Settings: settings})
