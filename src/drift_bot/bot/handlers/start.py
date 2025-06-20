from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from ..keyboards import start_keyboard
from ..callbacks import StartCallback

from ...core.enums import Role
from ...decorators import save_user


start_router = Router(name=__name__)


@start_router.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer(
        text="Здравствуйте, выберите кем вы являетесь ⬇️",
        reply_markup=start_keyboard()
    )


@start_router.callback_query(StartCallback.filter(F.role == Role.ADMIN))
@save_user(Role.ADMIN)
async def handle_admin(call: CallbackQuery) -> None:
    await call.message.answer("""<b><u>Доступные команды</u></b>
     * /create_competition - создаёт соревнование
     * /competitions - получает все соревнования
    """)


@start_router.callback_query(StartCallback.filter(F.role == Role.JUDGE))
@save_user(Role.JUDGE)
async def handle_judge(call: CallbackQuery) -> None:
    await call.message.answer("""<b><u>Доступные команды</u></b>
     * /active_competitions - получает все активные соревнования.
    """)


@start_router.callback_query(StartCallback.filter(F.role == Role.PILOT))
@save_user(Role.PILOT)
async def handle_pilot(call: CallbackQuery) -> None:
    await call.message.answer("""...
    """)
