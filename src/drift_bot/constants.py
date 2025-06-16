from typing import Literal

from enum import Enum, auto
from pathlib import Path


# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Переменные окружения
ENV_PATH = BASE_DIR / ".env"


class Role(Enum, str):
    """Возможные роли пользователей"""
    ADMIN = auto()      # Администратор
    REFEREE = auto()    # Судья
    PILOT = auto()      # Пилот, участник гонки
    DEVELOPER = auto()  # Доступен весь контент (используется для отладки)


class Criterion(Enum, str):
    """Судейские критерии"""
    STYLE = auto()  # Стиль
    ANGLE = auto()  # Угол
    LINE = auto()   # Траектория


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
