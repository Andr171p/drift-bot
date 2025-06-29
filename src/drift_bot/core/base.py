from typing import Generic, TypeVar, Optional, Any

from abc import ABC, abstractmethod
from datetime import datetime

from .domain import Judge, Pilot, Stage, Championship
from .dto import ActiveChampionship

T = TypeVar("T")


class CRUDRepository(Generic[T]):
    async def create(self, model: T) -> T: pass

    async def read(self, id: int | str) -> Optional[T]: pass

    async def read_all(self) -> list[T]: pass

    async def update(self, id: int | str, **kwargs) -> Optional[T]: pass

    async def delete(self, id: int | str) -> bool: pass


class ChampionshipRepository(CRUDRepository[Championship]):
    async def get_active(self) -> list[ActiveChampionship]: pass

    async def paginate(self, page: int, limit: int, is_active: bool = True) -> list[Championship]: pass

    async def count(self) -> int: pass

    async def get_stages(self, id: int) -> list[Stage]: pass

    async def get_by_user_id(self, user_id: int) -> list[Championship]: pass


class StageRepository(CRUDRepository[Stage]):
    async def get_nearest(self, championship_id: int, date: datetime) -> Optional[Stage]: pass


class PilotRepository(CRUDRepository[Pilot]):
    async def get_by_user_id(self, user_id: int) -> Optional[Pilot]: pass


class JudgeRepository(CRUDRepository[Judge]):
    async def get_by_user_id(self, user_id: int) -> Optional[Judge]: pass


class FileStorage(ABC):
    @abstractmethod
    async def upload_file(
            self,
            data: bytes,
            key: str,
            bucket: str,
            metadata: Optional[dict[str, Any]] = None
    ) -> None: pass

    @abstractmethod
    async def download_file(self, key: str, bucket: str) -> Optional[bytes]: pass

    @abstractmethod
    async def remove_file(self, key: str, bucket: str) -> None: pass
