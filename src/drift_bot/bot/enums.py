from enum import StrEnum


class Confirmation(StrEnum):
    YES = "yes"
    NO = "no"


class AdminEventAction(StrEnum):
    EDIT = "edit"
    DELETE = "delete"
    TOGGLE_REGISTRATION = "toggle_registration"
    REFEREES_LIST = "referees_list"
    PILOTS_LIST = "pilots_list"
