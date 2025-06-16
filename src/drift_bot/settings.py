import os
from dotenv import load_dotenv

from pydantic_settings import BaseSettings

from .constants import ENV_PATH


load_dotenv(ENV_PATH)


class BotSettings(BaseSettings):
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")


class S3Settings(BaseSettings):
    S3_URL: str = os.getenv("S3_URL")
    S3_USER: str = os.getenv("S3_USER")
    S3_PASSWORD: str = os.getenv("S3_PASSWORD")


class PostgresSettings(BaseSettings):
    PG_HOST: str = os.getenv("POSTGRES_HOST")
    PG_PORT: int = os.getenv("POSTGRES_PORT")
    PG_USER: str = os.getenv("POSTGRES_USER")
    PG_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    PG_DB: str = os.getenv("POSTGRES_DB")
    PG_DRIVER: str = "asyncpg"

    @property
    def sqlalchemy_url(self) -> str:
        return f"postgresql+{self.PG_DRIVER}://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"


class RedisSettings(BaseSettings):
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = os.getenv("REDIS_PORT")

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"


class Settings(BaseSettings):
    bot: BotSettings = BotSettings()
    postgres: PostgresSettings = PostgresSettings()
    s3: S3Settings = S3Settings()
    redis: RedisSettings = RedisSettings()
