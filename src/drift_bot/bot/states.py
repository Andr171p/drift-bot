from aiogram.fsm.state import StatesGroup, State


class ChampionshipForm(StatesGroup):
    """Форма для создания чемпионата."""
    title = State()         # Название мероприятия
    description = State()   # Описание (опционально)
    photo_id = State()      # Фото (опционально)
    document_id = State()   # Регламент соревнований (опционально)
    stages_count = State()  # Количество этапов


class StageForm(StatesGroup):
    """Форма для создания этапа."""
    championship_id = State()  # ID чемпионата
    number = State()           # Номер этапа
    title = State()            # Название
    description = State()      # Описание
    photo_id = State()         # Прикреплённое фото
    location = State()         # Место проведения
    map_link = State()         # Ссылка на карты
    date = State()             # Дата проведения


class JudgeForm(StatesGroup):
    """Форма для регистрации судьи."""
    stage_id = State()   # ID Этапа
    full_name = State()  # ФИО
    photo_id = State()   # ID файла с фото (опционально)
    criterion = State()  # Оцениваемый критерий


class CarForm(StatesGroup):
    """Форма для регистрации автомобиля."""
    type = State()
    name = State()
    plate = State()
    hp = State()


class PilotForm(StatesGroup):
    """Форма для регистрации пилота."""
    stage_id = State()
    full_name = State()
    age = State()
    description = State()
    team = State()
    cars = State()
    photo_id = State()
    number = State()
