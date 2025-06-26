from typing import Sequence, Optional, Generic, TypeVar, Union

import random
import secrets
from datetime import datetime, timedelta

from .enums import Role
from .base import FileStorage, CRUDRepository
from .domain import Championship, Stage,  Pilot, Referral, Judge, File, FileMetadata
from .exceptions import RanOutNumbersError, CodeExpiredError

from ..constants import CODE_LENGTH, DAYS_EXPIRE
from ..utils import generate_file_name


T = TypeVar("T", bound=Union[Championship, Stage, Pilot, Judge])


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


class CRUDService(Generic[T]):
    def __init__(
            self,
            crud_repository: CRUDRepository[T],
            file_storage: FileStorage
    ) -> None:
        self._crud_repository = crud_repository
        self._file_storage = file_storage

    async def create(
            self, model: T,
            files: Optional[list[File]] = None,
            bucket: Optional[str] = None
    ) -> T:
        files_metadata: list[FileMetadata] = []
        if files:
            for file in files:
                key = generate_file_name(file.format)
                await self._file_storage.upload_file(data=file.data, key=key, bucket=bucket)
                file_metadata = FileMetadata(
                    key=key,
                    bucket=bucket,
                    size=file.size,
                    format=file.format,
                    type=file.type,
                    uploaded_date=datetime.now()
                )
                files_metadata.append(file_metadata)
        model.files = files_metadata if files_metadata else model
        created_model = await self._crud_repository.create(model)
        return created_model

    async def read(self, id: int | str) -> tuple[T, Optional[list[File]]]:
        model = await self._crud_repository.read(id)
        if not model:
            return None
        if not model.files:
            return model
        files: list[File] = []
        for file in model.files:
            data = await self._file_storage.download_file(key=file.key, bucket=file.bucket)
            files.append(File(data=data, file_name=file.key))
        return model, files

    async def delete(self, id: int | str) -> bool:
        model = await self._crud_repository.read(id)
        if not model:
            return False
        is_deleted = await self._crud_repository.delete(id)
        if model.files:
            for file in model.files:
                await self._file_storage.remove_file(key=file.key, bucket=file.bucket)
        return is_deleted


class ReferralService:
    def __init__(self, referral_repository: CRUDRepository[Referral]) -> None:
        self._referral_repository = referral_repository

    @staticmethod
    def generate_code(role: Role) -> str:
        return f"{role.lower()}_{secrets.token_urlsafe(CODE_LENGTH)}"

    async def invite(self, stage_id: int, admin_id: int, role: Role) -> Referral:
        code = self.generate_code(role)
        referral = Referral(
            stage_id=stage_id,
            admin_id=admin_id,
            code=code,
            expires_at=datetime.now() + timedelta(days=DAYS_EXPIRE)
        )
        created_referral = await self._referral_repository.create(referral)
        return created_referral

    async def login(self, code: str) -> Optional[Referral]:
        now_time = datetime.now()
        referral = await self._referral_repository.read(code)
        if not referral:
            return None
        if referral.expires_at < now_time:
            raise CodeExpiredError("Referral code has expired")
        updated_referral = await self._referral_repository.update(referral.code, activated=True)
        return updated_referral
