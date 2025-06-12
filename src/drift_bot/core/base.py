from typing import Generic, TypeVar, Optional

from abc import ABC, abstractmethod


T = TypeVar("T")


class Repository(Generic[T]):
    async def create(self, entity: T) -> T: pass

    async def read(self, entity_id: int) -> Optional[T]: pass

    async def read_all(self) -> list[T]: pass

    async def update(self, entity_id: int, **kwargs) -> Optional[T]: pass

    async def delete(self, entity_id: int) -> bool: pass


class FileStorage(ABC):
    @abstractmethod
    async def upload_file(self, file_data: bytes, file_name: str, bucket_name: str) -> None: pass

    @abstractmethod
    async def download_file(self, file_name: str, bucket_name: str) -> Optional[bytes]: pass

    @abstractmethod
    async def remove_file(self, file_name: str, bucket_name: str) -> ...: pass
