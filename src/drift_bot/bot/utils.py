from aiogram.types import CallbackQuery

from ..core.domain import File


async def get_file(file_id: str, call: CallbackQuery) -> File:
    file = await call.bot.get_file(file_id=file_id)
    data = await call.bot.download(file)
    file_name = file.file_path
    return File(data=data, file_name=file_name)
