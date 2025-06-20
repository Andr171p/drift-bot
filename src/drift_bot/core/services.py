from typing import Sequence, Optional, Generic, TypeVar, Union
from collections.abc import AsyncIterator

import random
import secrets
from datetime import datetime, timedelta

from .enums import Role
from .base import FileStorage, CRUDRepository, Sender, UserRepository
from .domain import Event, Pilot, Photo, Referral, Judge, File
from .dto import (
    CreatedEvent,
    CreatedPilot,
    CreatedJudge,
    EventWithPhoto,
    PilotWithPhoto,
    JudgeWithPhoto
)
from .exceptions import RanOutNumbersError, CodeExpiredError

from ..constants import CODE_LENGTH, DAYS_EXPIRE


T = TypeVar("T", bound=Union[Event, Pilot, Judge])
R = TypeVar("R", bound=Union[EventWithPhoto, PilotWithPhoto, JudgeWithPhoto])
CreatedModel = Union[CreatedEvent, CreatedPilot, CreatedJudge]


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

    async def create(self, model: T, photo: Optional[Photo]) -> Optional[R]:
        if photo:
            await self._file_storage.upload_file(
                data=photo.data,
                file_name=photo.file_name,
                bucket=self._bucket
            )
            model.file_name = photo.file_name
        created_model: CreatedModel = await self._crud_repository.create(model)
        return await self.read(created_model.id)

    async def read(self, id: int) -> Optional[R]:
        model: CreatedModel = await self._crud_repository.read(id)
        file_name = model.file_name
        photo: Optional[Photo] = None
        if file_name:
            data = await self._file_storage.download_file(
                file_name=file_name,
                bucket=self._bucket
            )
            photo = Photo(
                data=data,
                file_name=file_name,
                format=file_name.split(".")[-1].lower()
            )
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
                data = await self._file_storage.download_file(
                    file_name=file_name,
                    bucket=self._bucket
                )
                photo = Photo(
                    data=data,
                    file_name=file_name,
                    format=file_name.split(".")[-1].lower()
                )
            yield model.attach_photo(photo)


class ReferralService:
    def __init__(self, referral_repository: CRUDRepository[Referral]) -> None:
        self._referral_repository = referral_repository

    @staticmethod
    def generate_code(role: Role) -> str:
        return f"{role.lower()}_{secrets.token_urlsafe(CODE_LENGTH)}"

    async def create_referral(self, event_id: int, admin_id: int, role: Role) -> Referral:
        code = self.generate_code(role)
        referral = Referral(
            event_id=event_id,
            admin_id=admin_id,
            code=code,
            expires_at=datetime.now() + timedelta(days=DAYS_EXPIRE)
        )
        created_referral = await self._referral_repository.create(referral)
        return created_referral

    async def get_referral(self, code: str) -> Optional[Referral]:
        now_time = datetime.now()
        referral = await self._referral_repository.read(code)
        if not referral:
            return None
        if referral.expires_at < now_time:
            raise CodeExpiredError("Referral code has expired")
        updated_referral = await self._referral_repository.update(referral.code, activated=True)
        return updated_referral


class NotificationService:
    def __init__(self, sender: Sender, user_repository: UserRepository) -> None:
        self._sender = sender
        self._user_repository = user_repository

    async def notify(
            self,
            user_id: int,
            message: str,
            file: Optional[File],
            **kwargs
    ) -> None:
        await self._sender.send(
            recipient_id=user_id,
            message=message,
            file=file,
            **kwargs
        )

    async def notify_by_role(
            self,
            role: Role,
            message: str,
            file: Optional[File],
            **kwargs
    ) -> None:
        users = await self._user_repository.get_by_role(role)
        for user in users:
            await self._sender.send(
                recipient_id=user.user_id,
                message=message,
                file=file,
                **kwargs
            )
