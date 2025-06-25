from enum import StrEnum


class Confirmation(StrEnum):
    YES = "yes"
    NO = "no"


class AdminChampionshipAction(StrEnum):
    EDIT = "edit"
    DELETE = "delete"
    ADD_STAGE = "add_stage"
