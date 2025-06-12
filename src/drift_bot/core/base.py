from typing import Generic, TypeVar, Optional


T = TypeVar("T")


class Repository(Generic[T]):
    async def create(self, entity: T) -> T: pass

    async def read(self, entity_id: int) -> Optional[T]: pass

    async def read_all(self) -> list[T]: pass

    async def update(self, entity_id: int, **kwargs) -> Optional[T]: pass

    async def delete(self, entity_id: int) -> bool: pass

