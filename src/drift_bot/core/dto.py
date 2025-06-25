from pydantic import BaseModel, ConfigDict


class ActiveChampionship(BaseModel):
    """Активный чемпионат."""
    id: int
    title: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
