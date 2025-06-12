from datetime import datetime

from .domain import Race


class CreatedRace(Race):
    created_at: datetime
    updated_at: datetime
