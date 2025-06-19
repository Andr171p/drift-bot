from typing import Sequence, Optional, Generic, TypeVar, Union
from collections.abc import AsyncIterator

import random

from .domain import Event, Pilot, Photo
from .dto import CreatedEvent, CreatedPilot, EventWithPhoto, PilotWithPhoto
from .base import FileStorage, CRUDRepository
from .exceptions import RanOutNumbersError


T = TypeVar("T", bound=Union[Event, Pilot])
R = TypeVar("R", bound=Union[EventWithPhoto, PilotWithPhoto])
CreatedModel = Union[CreatedEvent, CreatedPilot]


class NumberGenerator:
    def __init__(self, start: int, end: int) -> None:
        self._start = start
        self._end = end

    async def generate(self, used_numbers: Sequence[int]) -> int:
        """Генерирует уникальный и неповторяющийся номер"""
        if len(used_numbers) >= (self._end - self._start + 1):
            raise RanOutNumbersError("Ran out of numbers")
        while True:
            number = random.randint(self._start, self._end)
            if number not in used_numbers:
                return number


class CRUDService(Generic[T, R]):
    def __init__(
            self,
            crud_repository: CRUDRepository[T],
            file_storage: FileStorage,
            bucket: str
    ) -> None:
        self._crud_repository = crud_repository
        self._file_storage = file_storage
        self._bucket = bucket

    async def create(self, model: T, photo: Optional[Photo]) -> None:
        if photo:
            await self._file_storage.upload_file(
                data=photo.data,
                file_name=photo.file_name,
                bucket=self._bucket
            )
            model.file_name = photo.file_name
        await self._crud_repository.create(model)

    async def read(self, id: int) -> Optional[R]:
        model: CreatedModel = await self._crud_repository.read(id)
        file_name = model.file_name
        photo: Optional[Photo] = None
        if file_name:
            data = await self._file_storage.download_file(file_name=file_name, bucket=self._bucket)
            photo = Photo(data=data, file_name=file_name, format=file_name.split(".")[-1].lower())
        return model.attach_photo(photo)

    async def delete(self, id: int) -> bool:
        model: CreatedModel = await self._crud_repository.delete(id)
        is_deleted = False
        if model:
            await self._file_storage.remove_file(file_name=model.file_name, bucket=self._bucket)
            is_deleted = True
        return is_deleted

    async def read_all(self) -> AsyncIterator[R]:
        models: list[CreatedModel] = await self._crud_repository.read_all()
        for model in models:
            file_name = model.file_name
            photo: Optional[Photo] = None
            if file_name:
                data = await self._file_storage.download_file(file_name=file_name, bucket=self._bucket)
                photo = Photo(data=data, file_name=file_name, format=file_name.split(".")[-1].lower())
            yield model.attach_photo(photo)
