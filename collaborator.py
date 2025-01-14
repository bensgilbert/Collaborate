import uuid

import fastapi
import pydantic

from model import *


class Collaborator(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    username: str

    cursor_position: Position = Position(column=0, line_number=0)
    cursor_secondary_positions: list[Position] = []

    room: "Room" = pydantic.Field(exclude=True)
    websocket: fastapi.WebSocket = pydantic.Field(exclude=True)


from room import Room
Collaborator.model_rebuild()
