import fastapi
import uvicorn

from collaborator import Collaborator
from event import *
from room import Room, RoomManager


app = fastapi.FastAPI()

room_manager = RoomManager()


@app.websocket("/collaborate")
async def collaborate(websocket: fastapi.WebSocket):
    await websocket.accept()

    collaborator: Collaborator | None = None

    async for json in websocket.iter_json():
        client_event = ClientEvent.validate_json(json)

        match client_event:
            case ClientChatEvent():
                assert collaborator

                await collaborator.room.send_json(
                    ServerChatEvent(
                        collaborator=collaborator,
                        message=client_event.message,
                    ).model_dump(by_alias=True, mode="json"),
                )

            case ClientCreateEvent():
                assert collaborator is None

                room = room_manager.create_room()

                collaborator = Collaborator(
                    username=client_event.username,
                    room=room,
                    websocket=websocket,
                )

                room.add_collaborator(collaborator)

                await room.send_json(
                    ServerSyncEvent(
                        collaborator=collaborator,
                        room=room,
                    ).model_dump(by_alias=True, mode="json"),
                )

            case ClientCursorEvent():
                assert collaborator

                collaborator.cursor_position = client_event.position
                collaborator.cursor_secondary_positions = client_event.secondary_positions

                await collaborator.room.send_json(
                    ServerCursorEvent(
                        collaborator=collaborator,
                    ).model_dump(by_alias=True, mode="json"),
                )

            case ClientInfoEvent():
                room = room_manager.get_room_by_roomcode(client_event.roomcode)

                await websocket.send_json(
                    ServerInfoEvent(
                        room=room,
                    ).model_dump(by_alias=True, mode="json"),
                )

            case ClientJoinEvent():
                assert collaborator is None

                room = room_manager.get_room_by_roomcode(client_event.roomcode)

                if room is None:
                    await websocket.send_json(
                        ServerErrorEvent().model_dump(by_alias=True, mode="json"),
                    )
                    continue

                collaborator = Collaborator(
                    username=client_event.username,
                    room=room,
                    websocket=websocket,
                )

                await room.send_json(
                    ServerJoinEvent(
                        collaborator=collaborator,
                    ).model_dump(by_alias=True, mode="json"),
                )

                room.add_collaborator(collaborator)

                await websocket.send_json(
                    ServerSyncEvent(
                        collaborator=collaborator,
                        room=room,
                    ).model_dump(by_alias=True, mode="json"),
                )

            case ClientLeaveEvent():
                assert collaborator

                room = collaborator.room

                await room.send_json(
                    ServerLeaveEvent(
                        collaborator=collaborator,
                    ).model_dump(by_alias=True, mode="json"),
                )

                room.remove_collaborator(collaborator)
                collaborator = None

            case ClientUpdateEvent():
                assert collaborator

                room = collaborator.room

                for change in client_event.changes:
                    room.code = room.code[:change.range_offset] + change.text + room.code[change.range_offset + change.range_length:]

                await room.send_json(
                    ServerUpdateEvent(
                        collaborator=collaborator,
                        changes=client_event.changes,
                    ).model_dump(by_alias=True, mode="json"),
                )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
