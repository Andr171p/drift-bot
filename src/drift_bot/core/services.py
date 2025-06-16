from typing import Sequence, Optional
from collections.abc import AsyncIterator

import random
from uuid import uuid4

from .domain import Event, Referee, Referral
from .dto import CreatedEvent, EventWithPhoto, PilotWithPhoto
from .base import EventRepository, FileStorage, CRUDRepository
from .exceptions import RanOutNumbersError

from ..constants import EVENTS_BUCKET, PILOTS_BUCKET, SUPPORTED_IMAGE_FORMATS


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
    def __init__(
            self,
            event_repository: EventRepository,
            referral_repository: CRUDRepository[Referral],
            file_storage: FileStorage
    ) -> None:
        self._event_repository = event_repository
        self._referral_repository = referral_repository
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
                bucket_name=EVENTS_BUCKET
            )
            event.photo_name = photo_name
        created_event = await self._event_repository.create(event)
        return created_event

    async def delete_event(self, event_id: int) -> bool:
        event = await self._event_repository.read(event_id)
        if event.image_file is not None:
            await self._file_storage.remove_file(
                file_name=event.image_file,
                bucket_name=EVENTS_BUCKET
            )
        is_deleted = await self._event_repository.delete(event_id)
        return is_deleted

    async def get_events(self, page: int, limit: int) -> AsyncIterator[EventWithPhoto]:
        events = await self._event_repository.paginate(page, limit)
        for event in events:
            photo_data: Optional[bytes] = None
            if event.photo_name:
                photo_data = await self._file_storage.download_file(
                    file_name=event.photo_name,
                    bucket_name=EVENTS_BUCKET
                )
            sending_event = EventWithPhoto(**event.model_dump(), photo_data=photo_data)
            yield sending_event

    async def get_last_event(self) -> Optional[EventWithPhoto]:
        last_event = await self._event_repository.get_last()
        photo_data: Optional[bytes] = None
        if last_event.photo_name:
            photo_data = await self._file_storage.download_file(
                file_name=last_event.photo_name,
                bucket_name=EVENTS_BUCKET
            )
        return EventWithPhoto(**last_event.model_dump(), photo_data=photo_data)

    async def get_pilots(self, event_id: int) -> AsyncIterator[PilotWithPhoto]:
        pilots = await self._event_repository.get_pilots(event_id)
        for pilot in pilots:
            photo_data = await self._file_storage.download_file(
                file_name=pilot.photo_name,
                bucket_name=PILOTS_BUCKET
            )
            yield PilotWithPhoto(**pilot.model_dump(), photo_data=photo_data)

    async def create_referral(self, event_id: int) -> ...:
        ...


class RefereeService:
    def __init__(
            self,
            referral_repository: CRUDRepository[Referral],
            referee_repository: CRUDRepository[Referee]
    ) -> None:
        self._referral_repository = referral_repository
        self._referee_repository = referee_repository

    async def register_for_event(self, referral_link: str, referee: Referee) -> ...:
        ...

    async def give_points(self) -> ...:
        ...
