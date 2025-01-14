import asyncio
import random

import typing

import pydantic


class Room(pydantic.BaseModel):
    code: str = ""
    roomcode: str
    people: list["Collaborator"] = []

    def add_collaborator(self, collaborator: "Collaborator"):
        self.people.append(collaborator)

    def remove_collaborator(self, collaborator: "Collaborator"):
        self.people.remove(collaborator)

    async def send_json(self, data: typing.Any):
        await asyncio.gather(*(person.websocket.send_json(data) for person in self.people))


class RoomManager:
    def __init__(self):
        self.roomcode_to_room: dict[str, Room] = {}
        self.roomcode_pool = [f"{i:04d}" for i in range(1_000, 10_000)]
        random.shuffle(self.roomcode_pool)

    def create_room(self) -> Room:
        roomcode = random.choice(self.roomcode_pool)
        self.roomcode_pool.remove(roomcode)
        room = Room(roomcode=roomcode)
        self.roomcode_to_room[roomcode] = room
        return room

    def get_room_by_roomcode(self, roomcode: str) -> Room | None:
        return self.roomcode_to_room.get(roomcode)

    def delete_room_by_roomcode(self, roomcode: str):
        del self.roomcode_to_room[roomcode]


from collaborator import Collaborator
Room.model_rebuild()
