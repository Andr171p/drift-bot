from enum import Enum


class ParseMode(Enum, str):
    HTML = "HTML"


class Confirmation(Enum, str):
    YES = "yes"
    NO = "no"
