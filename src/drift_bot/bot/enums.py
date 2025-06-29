from enum import StrEnum


class Confirmation(StrEnum):
    YES = "yes"
    NO = "no"


class AdminChampionshipAction(StrEnum):
    EDIT = "edit"
    DELETE = "delete"
    ADD_STAGE = "add_stage"                  # Добавить этап
    TOGGLE_ACTIVATION = "toggle_activation"  # Сделать активным / деактивировать


class ChampionshipAction(StrEnum):
    STAGES_SCHEDULE = "stages_schedule"    # Расписание этапов
    READ_REGULATIONS = "read_regulations"  # Ознакомится с регламентом
    NEAREST_STAGE = "nearest_stage"        # Ближайший этап


class AdminStageAction(StrEnum):
    DELETE = "delete"
    TOGGLE_REGISTRATION = "toggle_registration"  # Открыть / закрыть регистрацию
    INVITE_JUDGE = "invite_judge"                # Пригласить судей


class CalendarAction(StrEnum):
    PREVIOUS = "previous"
    NEXT = "next"
    TODAY = "today"
    IGNORE = "ignore"
    DAY = "day"
