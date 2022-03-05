from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket
from cruds import create_new_room, exit_room_by_id, join_room_by_id
from db.db import get_db
from db.db import Session
from schemas import Room as RoomSchema
from utils import class_to_json

router = APIRouter()

clients = {}

@router.post('/api/v1/room', response_model=RoomSchema)
async def create_room(db: Session = Depends(get_db)):
    room = create_new_room(db)
    return room

@router.websocket('/ws/room/{room_id}')
async def join_room(room_id: str, ws: WebSocket, user_name: str = 'anonymous', db: Session = Depends(get_db)):
    user, room = join_room_by_id(db, room_id, user_name)

    await ws.accept()
    key = ws.headers.get('sec-websocket-key')
    my_room = clients.get(room.room_id)
    if (my_room):
        my_room[key] = ws
    else:
        clients[room.room_id] = { key: ws }
        my_room = clients.get(room.room_id)

    await ws.send_json(class_to_json(room))
    for client in my_room.values():
        await client.send_json({'event': 'join_new_user', 'user': class_to_json(user)})

    try:
        while True:
            data: dict = await ws.receive_json()
            if not data.get('event'):
                continue

            event_name = data.get('event')
            if data.keys() == {'event', 'user_id', 'emotion'} and event_name == 'change_emotion':
                print(f"[ChangeEmotion] Room: {room_id} User: {data.get('user_id')} Emotion: {data.get('emotion')}")
                for client in my_room.values():
                    await client.send_json(data)
            if data.keys() == {'event', 'user_id', 'emotion', 'emoji'} and event_name == 'change_settiong_emoji':
                print(f"[ChangeSettingEmoji] Room: {room_id} User: {data.get('user_id')} Emotion: {data.get('emotion')} Emoji: {data.get('emoji')}")
                for client in my_room.values():
                    await client.send_json(data)
            if data.keys() == {'event', 'user_id', 'is_afk'} and event_name == 'turn_afk':
                print(f"[TurnAFK] Room: {room_id} User: {data.get('user_id')} Emotion: {data.get('is_afk')}")
                for client in my_room.values():
                    await client.send_json(data)
    except Exception as e:
        print(e)
        for client in my_room.values():
            await client.send_json({'event': 'exit_user', 'user': class_to_json(user)})
        exit_room_by_id(db, user.user_id)
        del clients[room.room_id][key]
