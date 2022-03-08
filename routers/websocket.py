import json
from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket
from cruds import exit_room_by_id, join_room_by_id
from db.db import get_db
from db.db import Session
from utils import class_to_json, create_dict_with_serial
from validations import allow_event, websocket_validator

clients = {}
user_list = {}

websocket_router = APIRouter()

@websocket_router.websocket('/room/{room_id}')
async def join_room(room_id: str, ws: WebSocket, user_name: str = 'anonymous', db: Session = Depends(get_db)):
    try:
        user, room = join_room_by_id(db, room_id, user_name)
        if user == None and room == None:
            return
        
        my_user_id = user.user_id
        my_room_id = room.room_id

        await ws.accept()

        my_info = create_default_user(my_user_id, user.name)

        my_room = clients.get(my_room_id)
        if (my_room):
            my_room[my_user_id] = ws
        else:
            clients[my_room_id] = { my_user_id: ws }
            my_room = clients.get(my_room_id)

        my_room_user = user_list.get(my_room_id)
        if (my_room_user):
            my_room_user[my_user_id] = my_info
        else:
            user_list[my_room_id] = { my_user_id: my_info }
            my_room_user = user_list.get(my_room_id)

        room_info_for_ws = create_dict_with_serial('room_info', {
            "room_id": my_room_id,
            "expired_at": room.expired_at,
            "created_at": room.created_at,
            "users": list(my_room_user.values())
        })
        join_new_user = create_dict_with_serial('json_new_user', my_info)
        await ws.send_json(room_info_for_ws)
        for client in my_room.values():
            await client.send_json(join_new_user)

        while True:
            data: dict = await ws.receive_json()
            event_name = data.get('event')
            if not event_name:
                continue
            if not event_name in allow_event:
                continue

            if websocket_validator[event_name](data):
                data['user_id'] = my_user_id
                for client in my_room.values():
                    await client.send_json(data)

    except Exception as e:
        print(e)
        exit_room_by_id(db, my_user_id)
        del clients[my_room_id][my_user_id]
        del user_list[my_room_id][my_user_id]
        exit_user = {
            'event': 'exit_user',
            'user': class_to_json(user)
        }
        for client in my_room.values():
            await client.send_json(exit_user)

def create_default_user(user_id: str, user_name: str) -> dict:
    return {
        'user_id': user_id,
        'name': user_name,
        'emotion': 'neutral',
        'emoji': {
            'neutral': 0,
            'happy': 0,
            'sad': 0,
            'angry': 0,
            'fearful': 0,
            'disgusted': 0,
            'surprised': 0
        },
        'is_afk': False,
        'is_speaking': False
    }
