from typing import Literal

from enum import StrEnum
from pathlib import Path


# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Переменные окружения
ENV_PATH = BASE_DIR / ".env"


class Role(StrEnum):
    """Возможные роли пользователей"""
    ADMIN = "ADMIN"          # Администратор
    REFEREE = "REFEREE"      # Судья
    PILOT = "PILOT"          # Пилот, участник гонки
    DEVELOPER = "DEVELOPER"  # Доступен весь контент (используется для отладки)


class Criterion(StrEnum):
    """Судейские критерии"""
    STYLE = "STYLE"  # Стиль
    ANGLE = "ANGLE"  # Угол
    LINE = "LINE"    # Траектория


# Разрешённое количество попыток
ATTEMPT = Literal[1, 2]

# URL бота
BOT_NAME = "DriftBot_bot"
BOT_URL = f"https://t.me/{BOT_NAME}"

# Время жизни реферальной ссылки
REFERRAL_LIFE_TIME = 3  # Дней

# S3 бакеты для хранения файловых объектов
EVENT_BUCKET = "events"

# Поддерживаемые форматы изображения
SUPPORTED_IMAGE_FORMATS = {"png", "jpg", "jpeg"}

# Пагинация
FIRST_PAGE = 1
LIMIT = 3
