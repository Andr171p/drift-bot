from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from dishka.integrations.aiogram import FromDishka as Depends

from ..states import EventForm
from ..callbacks import ConfirmCallback
from ..constants import ParseMode, Confirmation
from ..keyboards import confirm_event_creation_kb

from ...core.domain import Event
from ...core.services import EventService


events_router = Router(name=__name__)


@events_router.message(Command("create-event"))
async def send_event_form(message: Message, state: FSMContext) -> None:
    await state.set_state(EventForm.title)
    await message.answer("Введите название мероприятия: ")


@events_router.message(EventForm.title)
async def enter_event_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(EventForm.description)
    await message.answer("Добавьте описание (или нажмите /skip): ")


@events_router.message(EventForm.description)
async def enter_event_description(message: Message, state: FSMContext) -> None:
    if message.text.lower() != "/skip":
        await state.update_data(description=message.text)
    await state.set_state(EventForm.photo_id)
    await message.answer("Загрузите фото (в формате png, jpg, jpeg): ")


@events_router.message(EventForm.photo_id, F.photo)
async def enter_event_photo(message: Message, state: FSMContext) -> None:
    photo = message.photo[-1]
    photo_id = photo.file_id
    await state.update_data(photo_id=photo_id)
    await state.set_state(EventForm.location)
    await message.answer("Укажите место проведения: ")


@events_router.message(EventForm.location)
async def enter_event_location(message: Message, state: FSMContext) -> None:
    await state.update_data(location=message.text)
    await state.set_state(EventForm.map_link)
    await message.answer("Добавьте ссылку на карту (Google Maps, Яндекс.карты, 2Gis): ")


@events_router.message(EventForm.map_link)
async def enter_event_map_link(message: Message, state: FSMContext) -> None:
    await state.update_data(map_link=message.text)
    await state.set_state(EventForm.date)
    await message.answer("Укажите дату и время мероприятия (в формате Число.Месяц.Год Часы.Минуты): ")


@events_router.message(EventForm.date)
async def enter_event_date(message: Message, state: FSMContext) -> None:
    date = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
    await state.update_data(date=date)
    data = await state.get_data()
    text = f"""
    📌 <b>Название:</b> {data["title"]}
    📝 <b>Описание:</b> {data.get("description", "Нет")}
    📍 <b>Место:</b> {data["location"]}
    🗺️ <b>Как добраться:</b> {data["map_link"]}
    🗓 <b>Дата:</b> {date.strftime('%d.%m.%Y %H:%M')}
    """
    await message.answer_photo(
        photo=data["photo_file"],
        caption=text,
        parse_mode=ParseMode.HTML,
        reply_markup=confirm_event_creation_kb()
    )
    await message.answer("Подтвердите создание мероприятия (Да/нет): ")


@events_router.message(ConfirmCallback.filter(F.confirmation == Confirmation.NO))
async def cancel_event_creation(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ Создание отменено.")


@events_router.message(ConfirmCallback.filter(F.confirmation == Confirmation.YES))
async def create_event(
        message: Message,
        state: FSMContext,
        event_service: Depends[EventService]
) -> None:
    data = await state.get_data()
    event = Event(
        title=data["title"],
        description=data["description"],
        location=data["location"],
        map_link=data["map_link"],
        date=data["date"]
    )
    photo_file = await message.bot.get_file(file_id=data["photo_id"])
    photo_data = await message.bot.download(file=photo_file)
    photo_format = photo_file.file_path.split(".")[-1].lower()
    await event_service.create_event(event, photo_data=photo_data.read(), photo_format=photo_format)
    await message.answer("✅ Мероприятие создано!")
