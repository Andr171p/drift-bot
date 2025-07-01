from enum import StrEnum, IntEnum, auto


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


class CarType(StrEnum):
    """Тип автомобиля"""
    DRIFT = "DRIFT"          # Авто на котором пилот принимает участие
    TECHNICAL = "TECHNICAL"  # 'Техничка' (для механика и прочего персонала)


class FileType(StrEnum):
    """Тип файла"""
    PHOTO = "PHOTO"
    DOCUMENT = "DOCUMENT"


class QualificationAttempt(IntEnum):
    """Квалификационная попытка"""
    first = auto()
    second = auto()
