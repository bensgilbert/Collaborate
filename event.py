import typing

import pydantic

from collaborator import Collaborator
from model import *
from room import Room


class ClientEvent:
    _event_type_to_event_class: dict[str, pydantic.BaseModel] = {}

    @staticmethod
    def type(event_type):
        def wrapper(event_class):
            ClientEvent._event_type_to_event_class[event_type] = event_class
            return event_class
        return wrapper

    @staticmethod
    def validate_json(json: dict[str, typing.Any]):
        event_type = json["type"]
        event_data = json["data"]
        return ClientEvent._event_type_to_event_class[event_type].model_validate(event_data)


@ClientEvent.type("chat")
class ClientChatEvent(pydantic.BaseModel):
    message: str


@ClientEvent.type("create")
class ClientCreateEvent(pydantic.BaseModel):
    username: str


@ClientEvent.type("cursor")
class ClientCursorEvent(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(alias_generator=pydantic.alias_generators.to_camel)

    position: Position
    secondary_positions: list[Position]


@ClientEvent.type("info")
class ClientInfoEvent(pydantic.BaseModel):
    roomcode: str


@ClientEvent.type("join")
class ClientJoinEvent(pydantic.BaseModel):
    username: str
    roomcode: str


@ClientEvent.type("leave")
class ClientLeaveEvent(pydantic.BaseModel):
    pass


@ClientEvent.type("update")
class ClientUpdateEvent(pydantic.BaseModel):
    changes: list[Change]


class ServerEvent(pydantic.BaseModel):
    _event_class_to_event_type: typing.ClassVar[dict[pydantic.BaseModel, str]] = {}

    @staticmethod
    def type(event_type):
        def wrapper(event_class):
            ServerEvent._event_class_to_event_type[event_class] = event_type
            return event_class
        return wrapper
    
    def model_dump(self, *, mode = 'python', include = None, exclude = None, context = None, by_alias = False, exclude_unset = False, exclude_defaults = False, exclude_none = False, round_trip = False, warnings = True, serialize_as_any = False):
        model = super().model_dump(mode=mode, include=include, exclude=exclude, context=context, by_alias=by_alias, exclude_unset=exclude_unset, exclude_defaults=exclude_defaults, exclude_none=exclude_none, round_trip=round_trip, warnings=warnings, serialize_as_any=serialize_as_any)
        return {
            "type": ServerEvent._event_class_to_event_type[self.__class__],
            "data": model,
        }

    def model_dump_json(self, *, indent = None, include = None, exclude = None, context = None, by_alias = False, exclude_unset = False, exclude_defaults = False, exclude_none = False, round_trip = False, warnings = True, serialize_as_any = False):
        model = super().model_dump_json(indent=indent, include=include, exclude=exclude, context=context, by_alias=by_alias, exclude_unset=exclude_unset, exclude_defaults=exclude_defaults, exclude_none=exclude_none, round_trip=round_trip, warnings=warnings, serialize_as_any=serialize_as_any)
        return f"""{{"type":"{ServerEvent._event_class_to_event_type[self.__class__]}","data":{model}}}"""


@ServerEvent.type("chat")
class ServerChatEvent(ServerEvent):
    collaborator: Collaborator
    message: str


@ServerEvent.type("cursor")
class ServerCursorEvent(ServerEvent):
    collaborator: Collaborator


@ServerEvent.type("error")
class ServerErrorEvent(ServerEvent):
    pass


@ServerEvent.type("info")
class ServerInfoEvent(ServerEvent):
    room: Room | None


@ServerEvent.type("join")
class ServerJoinEvent(ServerEvent):
    collaborator: Collaborator


@ServerEvent.type("leave")
class ServerLeaveEvent(ServerEvent):
    collaborator: Collaborator


@ServerEvent.type("sync")
class ServerSyncEvent(ServerEvent):
    collaborator: Collaborator
    room: Room


@ServerEvent.type("update")
class ServerUpdateEvent(ServerEvent):
    collaborator: Collaborator
    changes: list[Change]
