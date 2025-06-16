from typing import Generic, TypeVar, Optional, Any

from abc import ABC, abstractmethod

from .domain import Event, Referee, Pilot


T = TypeVar("T")


class CRUDRepository(Generic[T]):
    async def create(self, model: T) -> T: pass

    async def read(self, id: int | str) -> Optional[T]: pass

    async def read_all(self) -> list[T]: pass

    async def update(self, id: int | str, **kwargs) -> Optional[T]: pass

    async def delete(self, id: int | str) -> bool: pass


class EventRepository(CRUDRepository[Event]):
    async def paginate(self, page: int, limit: int) -> list[Event]: pass

    async def get_last(self) -> Event: pass

    async def get_referees(self, event_id: int) -> list[Referee]: pass

    async def get_pilots(self, event_id: int) -> list[Pilot]: pass


class FileStorage(ABC):
    @abstractmethod
    async def upload_file(
            self,
            file_data: bytes,
            file_name: str,
            bucket_name: str,
            metadata: Optional[dict[str, Any]] = None
    ) -> None: pass

    @abstractmethod
    async def download_file(self, file_name: str, bucket_name: str) -> Optional[bytes]: pass

    @abstractmethod
    async def remove_file(self, file_name: str, bucket_name: str) -> ...: pass
