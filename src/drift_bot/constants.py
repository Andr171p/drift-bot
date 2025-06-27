from typing import Literal

from pathlib import Path

from .core.enums import Criterion


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
CHAMPIONSHIPS_BUCKET = "championships"
STAGES_BUCKET = "stages"
PILOTS_BUCKET = "pilots"
JUDGES_BUCKET = "judges"

# Поддерживаемые форматы изображения
PHOTO_FORMATS: set[str] = {"png", "jpg", "jpeg"}
DOCUMENT_FORMATS: set[str] = {"doc", "docx", "pdf"}

# Пагинация
FIRST_PAGE = 1
LIMIT = 3

# Реферальная система:
CODE_LENGTH = 16
DAYS_EXPIRE = 3

ADMIN_USERNAMES: list[str] = []

# Кеширование
MAX_SIZE = 1000
TTL = 1

# Соревнования
MIN_STAGES_COUNT = 1
MIN_TITLE_LENGTH = 1
MAX_TITLE_LENGTH = 100

CRITERION2TEXT: dict[Criterion, str] = {
    Criterion.ANGLE: "<b>Угол</b>",
    Criterion.LINE: "<b>Траектория</b>",
    Criterion.STYLE: "<b>Стиль</b>"
}

# Названия месяцев
MONTH_NAMES: list[str] = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]
# Название дней недели
WEEKDAY_NAMES: list[str] = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

