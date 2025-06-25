from enum import StrEnum


class Confirmation(StrEnum):
    YES = "yes"
    NO = "no"


class AdminChampionshipAction(StrEnum):
    EDIT = "edit"
    DELETE = "delete"
    ADD_STAGE = "add_stage"  # Добавить этап


class AdminStageAction(StrEnum):
    DELETE = "delete"
    TOGGLE_REGISTRATION = "toggle_registration"
    INVITE_JUDGE = "invite_judge"
