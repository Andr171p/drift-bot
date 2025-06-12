from typing import Literal

from pathlib import Path


# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Переменные окружения
ENV_PATH = BASE_DIR / ".env"


# Разрешённое количество попыток
ATTEMPT = Literal[1, 2]

CRITERION = Literal[
    "STYLE",  # Судья стиля
    "ANGLE",  # Судья угла
    "LINE"  # Судья траектории
]
