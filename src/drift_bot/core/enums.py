from enum import StrEnum


class Role(StrEnum):
    """Возможные роли пользователей"""
    ADMIN = "ADMIN"          # Администратор
    JUDGE = "JUDGE"          # Судья
    PILOT = "PILOT"          # Пилот, участник гонки
    DEVELOPER = "DEVELOPER"  # Доступен весь контент (используется для отладки)


class Criterion(StrEnum):
    """Судейские критерии"""
    STYLE = "STYLE"  # Стиль
    ANGLE = "ANGLE"  # Угол
    LINE = "LINE"    # Траектория


class SendingStatus(StrEnum):
    """Статус отправки"""
    DELIVERED = "DELIVERED"
    NOT_DELIVERED = "NOT_DELIVERED"
    ERROR = "ERROR"
