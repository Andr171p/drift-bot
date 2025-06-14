from typing import Sequence, Optional

import random

from .domain import Race
from .dto import RaceCreation, CreatedRace, RaceRefactoring
from .base import FileStorage, CRUDRepository
from .exceptions import (
    RanOutNumbersError,
    CreationError,
    UploadingFileError
)


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


class RaceService:
    def __init__(
            self,
            race_repository: CRUDRepository[Race],
            file_storage: FileStorage
    ) -> None:
        self._race_repository = race_repository
        self._file_storage = file_storage

    async def create_race(self, race_creation: RaceCreation) -> Optional[CreatedRace]:
        race = Race.model_validate(race_creation)
        try:
            created_race = self._race_repository.create(race)
        except CreationError:
            return None
        try:
            await self._file_storage.upload_file(
                file_data=race_creation.image,
                file_name=race_creation.image_file_name,
                bucket_name="races"
            )
        except UploadingFileError:
            return None
        return created_race

    async def refactor_race(self, race_id: int, race_refactoring: RaceRefactoring) -> CreatedRace:
        updated_race = await self._race_repository.update(race_id, **race_refactoring.model_dump())
