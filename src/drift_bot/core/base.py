from typing import Generic, TypeVar, Optional

from abc import ABC, abstractmethod


T = TypeVar("T")


class CRUDRepository(Generic[T]):
    async def create(self, model: T) -> T: pass

    async def read(self, id: int) -> Optional[T]: pass

    async def read_all(self) -> list[T]: pass

    async def update(self, id: int, **kwargs) -> Optional[T]: pass

    async def delete(self, id: int) -> bool: pass


class FileStorage(ABC):
    @abstractmethod
    async def upload_file(self, file_data: bytes, file_name: str, bucket_name: str) -> None: pass

    @abstractmethod
    async def download_file(self, file_name: str, bucket_name: str) -> Optional[bytes]: pass

    @abstractmethod
    async def remove_file(self, file_name: str, bucket_name: str) -> ...: pass
