from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.websockets import WebSocket
from cruds import change_emotion, change_setting_emoji, create_new_room, exit_room_by_id, join_room_by_id, switch_afk
from db.db import get_db
from db.db import Session
from schemas import CreateRoom, Room as RoomSchema
from utils import class_to_json


router = APIRouter()

clients = {}

@router.post('/api/v1/room', response_model=RoomSchema)
async def create_room(payload: CreateRoom, db: Session = Depends(get_db)):
    room = create_new_room(db, payload.limit)
    return room

@router.websocket('/ws/room/{room_id}')
async def join_room(room_id: str, ws: WebSocket, user_name: str = 'anonymous', db: Session = Depends(get_db)):
    try:
        user, room = join_room_by_id(db, room_id, user_name)
        if user == None and room == None:
            return

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

        while True:
            data: dict = await ws.receive_json()
            if not data.get('event'):
                continue

            event_name = data.get('event')
            if data.keys() == {'event', 'user_id', 'emotion'} and event_name == 'change_emotion':
                if user.user_id == data.get('user_id'):
                    changed_user = change_emotion(db, data.get('user_id'), data.get('emotion'))
                    if changed_user:
                        for client in my_room.values():
                            await client.send_json(changed_user.dict())

            if data.keys() == {'event', 'user_id', 'emotion', 'emoji'} and event_name == 'change_settiong_emoji':
                if user.user_id == data.get('user_id'):
                    changed_user = change_setting_emoji(db, data.get('user_id'), data.get('emotion'), data.get('emoji'))
                    if changed_user:
                        for client in my_room.values():
                            await client.send_json(changed_user.dict())

            if data.keys() == {'event', 'user_id', 'is_afk'} and event_name == 'switch_afk':
                if user.user_id == data.get('user_id'):
                    changed_user = switch_afk(db, data.get('user_id'), data.get('is_afk'))
                    if changed_user:
                        for client in my_room.values():
                            await client.send_json(changed_user.dict())

    except Exception as e:
        print(e)
        exit_room_by_id(db, user.user_id)
        del clients[room.room_id][key]
        for client in my_room.values():
            await client.send_json({'event': 'exit_user', 'user': class_to_json(user)})
