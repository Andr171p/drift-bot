from typing import Sequence, Optional, Any
from collections.abc import AsyncGenerator

import random
from uuid import uuid4

from .domain import Event
from .dto import CreatedEvent, ReceivedEvent
from .base import EventRepository, FileStorage
from .exceptions import RanOutNumbersError

from ..constants import EVENT_BUCKET, SUPPORTED_IMAGE_FORMATS


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


class EventService:
    def __init__(self, event_repository: EventRepository, file_storage: FileStorage) -> None:
        self._event_repository = event_repository
        self._file_storage = file_storage

    async def create_event(
            self,
            event: Event,
            photo_data: Optional[bytes] = None,
            photo_format: Optional[str] = None
    ) -> Optional[CreatedEvent]:
        if photo_format not in SUPPORTED_IMAGE_FORMATS:
            raise ValueError("Unsupported image format")
        if photo_data:
            photo_name = f"{uuid4()}.{photo_format}"
            await self._file_storage.upload_file(
                file_data=photo_data,
                file_name=photo_name,
                bucket_name=EVENT_BUCKET
            )
            event.photo_name = photo_name
        created_event = await self._event_repository.create(event)
        return created_event

    async def delete_event(self, event_id: int) -> bool:
        event = await self._event_repository.read(event_id)
        if event.image_file is not None:
            await self._file_storage.remove_file(
                file_name=event.image_file,
                bucket_name=EVENT_BUCKET
            )
        is_deleted = await self._event_repository.delete(event_id)
        return is_deleted

    async def get_events(self, page: int, limit: int) -> AsyncGenerator[ReceivedEvent, Any]:
        events = await self._event_repository.paginate(page, limit)
        for event in events:
            photo: Optional[bytes] = None
            if event.photo_file:
                photo = await self._file_storage.download_file(
                    file_name=event.image_file,
                    bucket_name=EVENT_BUCKET
                )
            received_event = ReceivedEvent(**event.model_dump(), photo=photo)
            yield received_event

    async def get_last_event(self) -> Optional[ReceivedEvent]:
        events = await self._event_repository.read_all()
        last_event = events[-1]
        photo: Optional[bytes] = None
        if last_event.image_file:
            photo = await self._file_storage.download_file(
                file_name=last_event.image_file,
                bucket_name=EVENT_BUCKET
            )
        return ReceivedEvent(**last_event.model_dump(), photo=photo)
