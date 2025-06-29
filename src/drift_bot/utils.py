from typing import Optional

from uuid import uuid4

from .core.enums import Role, FileType
from .core.domain import File


def parse_referral_code(url: str) -> str:
    """Парсит реферальный код из стартовой ссылки."""
    parts = url.split("start=")
    return parts[-1] if len(parts) > 1 else ""


def parse_role_from_code(code: str) -> Role:
    """Парсит роль пользователя из реферального кода."""
    return code.split("_")[0].upper()


def generate_file_name(format: str) -> str:
    """Генерирует уникальное имя для файла."""
    return f"{uuid4()}.{format}"


def find_target_file(files: list[File], target_type: FileType) -> Optional[File]:
    """Ищет заданный файл в коллекции файлов."""
    return next((file for file in files if file.type == target_type), None)
