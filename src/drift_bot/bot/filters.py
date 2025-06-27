from aiogram.filters import Filter
from aiogram.types import Message

from .types import FilteredFile

from ..core.enums import FileType


class FileFilter(Filter):
    def __init__(self, file_type: FileType) -> None:
        self.file_type = file_type

    async def __call__(self, message: Message) -> FilteredFile | bool:
        filtered_file: FilteredFile = {"skip": False}
        if message.text == "/skip":
            filtered_file["skip"] = True
            return filtered_file
        if self.file_type == FileType.PHOTO and message.photo:
            filtered_file["file_id"] = message.photo[-1].file_id
            return filtered_file
        elif self.file_type == FileType.DOCUMENT and message.document:
            filtered_file["file_id"] = message.document.file_id
            return filtered_file
        return False
