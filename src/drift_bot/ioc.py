from dishka import Provider, provide, Scope, from_context, make_async_container

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

from .settings import Settings


class AppProvider(Provider):
    config = from_context(provides=Settings, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_bot(self, config: Settings) -> Bot:
        return Bot(
            token=config.bot.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )


settings = Settings()

container = make_async_container(AppProvider(), context={Settings: settings})
