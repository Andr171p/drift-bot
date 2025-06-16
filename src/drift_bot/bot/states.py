from aiogram.fsm.state import StatesGroup, State


class EventForm(StatesGroup):
    title = State()          # Название мероприятия
    description = State()    # Описание (опционально)
    photo_id = State()       # Фото (опционально)
    location = State()       # Место проведения
    map_link = State()       # Ссылка на карту (опционально)
    date = State()           # Дата проведения
    confirm = State()        # Подтверждение данных
