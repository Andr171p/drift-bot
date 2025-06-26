from enum import StrEnum


class Confirmation(StrEnum):
    YES = "yes"
    NO = "no"


class AdminChampionshipAction(StrEnum):
    EDIT = "edit"
    DELETE = "delete"
    ADD_STAGE = "add_stage"                  # Добавить этап
    TOGGLE_ACTIVATION = "toggle_activation"  # Сделать активным / деактивировать


class AdminStageAction(StrEnum):
    DELETE = "delete"
    TOGGLE_REGISTRATION = "toggle_registration"  # Открыть / закрыть регистрацию
    INVITE_JUDGE = "invite_judge"
