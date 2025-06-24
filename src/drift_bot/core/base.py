from typing import Generic, TypeVar, Optional, Any

from abc import ABC, abstractmethod

from .enums import Role
from .domain import User, Judge, Pilot, File, Stage
from .dto import CreatedEvent, CreatedPilot, CreatedJudge


T = TypeVar("T")


class CRUDRepository(Generic[T]):
    async def create(self, model: T) -> T: pass

    async def read(self, id: int | str) -> Optional[T]: pass

    async def read_all(self) -> list[T]: pass

    async def update(self, id: int | str, **kwargs) -> Optional[T]: pass

    async def delete(self, id: int | str) -> bool: pass


class UserRepository(CRUDRepository[User]):
    async def get_by_role(self, role: Role) -> list[User]: pass


class StageRepository(CRUDRepository[Stage]):
    async def paginate(self, page: int, limit: int) -> list[CreatedEvent]: pass

    async def get_last(self) -> CreatedEvent: pass

    async def get_active(self) -> list[CreatedEvent]: pass

    async def get_judges(self, event_id: int) -> list[Judge]: pass

    async def get_pilots(self, event_id: int) -> list[Pilot]: pass


class PilotRepository(CRUDRepository[Pilot]):
    async def get_by_user_id(self, user_id: int) -> Optional[CreatedPilot]: pass


class JudgeRepository(CRUDRepository[Judge]):
    async def get_by_user_id(self, user_id: int) -> Optional[CreatedJudge]: pass


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


class Sender(ABC):
    @abstractmethod
    async def send(
            self,
            recipient_id: int,
            message: str,
            file: Optional[File],
            **kwargs
    ) -> None: pass
