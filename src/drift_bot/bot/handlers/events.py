from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message, CallbackQuery, BufferedInputFile

from dishka.integrations.aiogram import FromDishka as Depends

from ..states import EventForm
from ..enums import Confirmation, AdminEventAction
from ..callbacks import ConfirmCallback, AdminEventCallback
from ..keyboards import confirm_event_creation_kb, admin_event_actions_kb

from ...core.enums import Role
from ...core.domain import Event, Photo
from ...core.dto import EventWithPhoto
from ...core.services import CRUDService, ReferralService
from ...core.base import EventRepository, FileStorage
from ...templates import SUBMIT_EVENT_CREATION_MESSAGE
from ...constants import EVENTS_BUCKET, BOT_URL


events_router = Router(name=__name__)


@events_router.message(Command("create_event"))
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
    await state.set_state(EventForm.file_id)
    await message.answer("Загрузите фото (в формате png, jpg, jpeg): ")


@events_router.message(EventForm.file_id, F.photo)
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
    text = SUBMIT_EVENT_CREATION_MESSAGE.format(
        title=data["title"],
        description=data["description"],
        location=data["location"],
        map_link=data["map_link"],
        date=data["date"].strftime('%d.%m.%Y %H:%M')
    )
    await message.answer_photo(
        photo=data["photo_id"],
        caption=text,
        parse_mode=ParseMode.HTML,
    )
    await message.answer(
        text="Подтвердите создание мероприятия (Да/нет): ",
        reply_markup=confirm_event_creation_kb()
    )


@events_router.callback_query(ConfirmCallback.filter(F.confirmation == Confirmation.NO))
async def cancel_event_creation(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer("❌ Создание отменено.")


@events_router.callback_query(ConfirmCallback.filter(F.confirmation == Confirmation.YES))
async def create_event(
        call: CallbackQuery,
        state: FSMContext,
        event_repository: Depends[EventRepository],
        file_storage: Depends[FileStorage]
) -> None:
    event_service = CRUDService[Event, EventWithPhoto](
        crud_repository=event_repository,
        file_storage=file_storage,
        bucket=EVENTS_BUCKET
    )
    data = await state.get_data()
    event = Event(
        title=data["title"],
        description=data["description"],
        location=data["location"],
        map_link=data["map_link"],
        date=data["date"]
    )
    file = await call.bot.get_file(file_id=data["file_id"])
    file_data = await call.bot.download(file=file)
    file_format = file.file_path.split(".")[-1].lower()
    photo = Photo(data=file_data.read(), format=file_format)
    await event_service.create(event, photo)
    await call.message.answer("✅ Мероприятие создано!")


@events_router.message(Command("events"))
async def send_events(
        message: Message,
        event_repository: Depends[EventRepository],
        file_storage: Depends[FileStorage]
) -> None:
    event_service = CRUDService[Event, EventWithPhoto](
        crud_repository=event_repository,
        file_storage=file_storage,
        bucket=EVENTS_BUCKET
    )
    async for event in event_service.read_all():
        text = EVENT_TEMPLATE.format(
            title=event.title,
            description=event.description,
            location=event.location,
            map_link=event.map_link,
            date=event.map_link
        )
        photo = event.photo
        await message.answer_photo(
            photo=BufferedInputFile(file=photo.data, filename=f"{event.title}.{photo.format}"),
            caption=text,
            reply_markup=admin_event_actions_kb(event_id=event.id, active=event.active)
        )


@events_router.callback_query(
    AdminEventCallback.filter(F.action == AdminEventAction.TOGGLE_REGISTRATION)
)
async def toggle_registration(
        call: CallbackQuery,
        callback_data: AdminEventCallback,
        event_repository: Depends[EventRepository]
) -> None:
    event_id = callback_data.event_id
    event = await event_repository.read(event_id)
    active = True
    if event.active:
        active = False
    updated_event = await event_repository.update(event_id, active=active)
    text = EVENT_TEMPLATE.format(
        title=updated_event.title,
        description=updated_event.description,
        location=updated_event.location,
        map_link=updated_event.map_link,
        date=updated_event.map_link
    )
    await call.message.answer_photo(
        photo=BufferedInputFile(file=event.photo_data, filename=f"{event.title}.jpg"),
        caption=text,
        reply_markup=admin_event_actions_kb(event_id=event_id, active=updated_event.active)
    )


@events_router.callback_query(
    AdminEventCallback.filter(F.action == AdminEventAction.INVITE_REFEREE)
)
async def invite_referee(
        call: CallbackQuery,
        callback_data: AdminEventCallback,
        referral_service: Depends[ReferralService]
) -> None:
    referral = await referral_service.create_referral(
        event_id=callback_data.event_id,
        admin_id=call.message.from_user.id,
        role=Role.REFEREE
    )
    referral_link = f"{BOT_URL}?start={referral.code}"
    await call.message.answer(f"Ваша реферальная ссылка:\n<code>{referral_link}</code>")
