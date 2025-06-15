from typing import Optional

from datetime import datetime

from .domain import Event


class CreatedEvent(Event):
    created_at: datetime
    updated_at: datetime


class ReceivedEvent(CreatedEvent):
    image: Optional[bytes]
