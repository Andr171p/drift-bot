from aiogram.fsm.state import StatesGroup, State


class EventForm(StatesGroup):
    title = State()        # Название мероприятия
    description = State()  # Описание (опционально)
    file_id = State()      # Фото (опционально)
    location = State()     # Место проведения
    map_link = State()     # Ссылка на карту (опционально)
    date = State()         # Дата проведения
    confirm = State()      # Подтверждение данных


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
