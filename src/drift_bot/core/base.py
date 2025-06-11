from abc import ABC, abstractmethod


class PilotRepository(ABC):
    @abstractmethod
    async def create(self, ) -> int: pass

    @abstractmethod
    async def read(self, pilot_id: int) -> ...: pass

    @abstractmethod
    async def read_all(self, ) -> list[...]: pass

    @abstractmethod
    async def update(self, ) -> ...: pass

    @abstractmethod
    async def delete(self, ) -> bool: pass
