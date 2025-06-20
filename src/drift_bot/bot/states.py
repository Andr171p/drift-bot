from aiogram.fsm.state import StatesGroup, State


class CompetitionForm(StatesGroup):
    title = State()         # Название мероприятия
    description = State()   # Описание (опционально)
    photo_id = State()      # Фото (опционально)
    document_id = State()   # Регламент соревнований (опционально)
    stages_count = State()  # Количество этапов


class JudgeForm(StatesGroup):
    event_id = State()   # ID ивента
    full_name = State()  # ФИО
    file_id = State()    # ID файла с фото (опционально)
    criterion = State()  # Оцениваемый критерий


class PilotForm(StatesGroup):
    event_id = State()
    full_name = State()
    age = State()
    description = State()
    team = State()
    file_id = State()
    car = State()
