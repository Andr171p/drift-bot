from .services import NumberGenerator
from .dto import PilotWithPhoto, PilotRegistration
from .services import CRUDService
from .base import PilotRepository, FileStorage
from .domain import Pilot, Photo

from ..constants import PILOTS_BUCKET


class PilotRegistrationUseCase:
    def __init__(
            self,
            pilot_repository: PilotRepository,
            file_storage: FileStorage
    ) -> None:
        self._pilot_repository = pilot_repository
        self._pilot_service = CRUDService[Pilot, PilotWithPhoto](
            crud_repository=pilot_repository,
            file_storage=file_storage,
            bucket=PILOTS_BUCKET
        )
        self._number_generator = NumberGenerator(start=..., end=...)

    async def execute(self, pilot_registration: PilotRegistration, photo: Photo) -> PilotWithPhoto:
        created_pilots = await self._pilot_repository.get_by_event_id(pilot_registration.event_id)
        used_numbers = [created_pilot.number for created_pilot in created_pilots]
        number = self._number_generator.generate(used_numbers)
        pilot = Pilot(
            event_id=pilot_registration.event_id,
            full_name=pilot_registration.full_name,
            age=pilot_registration.age,
            description=pilot_registration.description,
            file_name=pilot_registration.file_name,
            car=pilot_registration.car,
            number=number
        )
        pilot_with_photo = await self._pilot_service.create(pilot, photo)
        return pilot_with_photo


class GivePointsUseCase:
    def __init__(self) -> None:
        ...

    async def execute(self, ) -> ...:
        ...

