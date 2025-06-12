import os
from dotenv import load_dotenv

from pydantic_settings import BaseSettings

from .constants import ENV_PATH


load_dotenv(ENV_PATH)


class BotSettings(BaseSettings):
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")


class Settings(BaseSettings):
    bot: BotSettings = BotSettings()
