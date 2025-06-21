from typing import Literal

from pathlib import Path


# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Переменные окружения
ENV_PATH = BASE_DIR / ".env"

# Разрешённое количество попыток
ATTEMPT = Literal[1, 2]

# URL бота
BOT_NAME = "DriftBot_bot"
BOT_URL = f"https://t.me/{BOT_NAME}"

# Время жизни реферальной ссылки
REFERRAL_LIFE_TIME = 3  # Дней

# S3 бакеты для хранения файловых объектов
COMPETITIONS_BUCKET = "competitions"
PILOTS_BUCKET = "pilots"
JUDGES_BUCKET = "judges"

# Поддерживаемые форматы изображения
SUPPORTED_IMAGE_FORMATS = {"png", "jpg", "jpeg"}

# Пагинация
FIRST_PAGE = 1
LIMIT = 3

# Реферальная система:
CODE_LENGTH = 16
DAYS_EXPIRE = 3

ADMIN_USERNAMES = []

# Кеширование
MAX_SIZE = 1000
TTL = 1
