from enum import StrEnum

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_pascal


class EventTypes(StrEnum):
    DEGRADES = "DEGRADES"


class Degrade(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_pascal, populate_by_name=True, use_enum_values=True
    )
    type: str
    reason: str


class DegradeMessage(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_pascal, populate_by_name=True, use_enum_values=True
    )
    message_id: str
    timestamp: int
    event_type: EventTypes = EventTypes.DEGRADES
    degrades: list[Degrade]
