import asyncio
import threading
import time
from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket
from cruds import exit_room_by_id, exit_room_discord_user, join_room_by_id, join_room_discord_user
from db.db import get_db
from db.db import Session
from utils import class_to_json
from validations import allow_event, websocket_request_validator
from websocket_funcs import clients, user_list, websocket_funcs
from schemas import Room as RoomSchema

websocket_router = APIRouter()

@websocket_router.websocket('/room/{room_id}')
async def join_room(room_id: str, ws: WebSocket, user_name: str = 'anonymous', db: Session = Depends(get_db)):
    try:
        user, room = join_room_by_id(db, room_id, user_name)
        if user == None and room == None:
            return
        if room.is_discord_room:
            return
        
        my_user_id = user.user_id
        await core_websocket_func(ws, room, my_user_id, user_name)

    except Exception as e:
        print(e)
        exit_room_by_id(db, my_user_id)
        del clients[room_id][my_user_id]
        del user_list[room_id][my_user_id]
        exit_user = {
            'event': 'exit_user',
            'user': class_to_json(user)
        }
        for client in clients[room_id].values():
            await client.send_json(exit_user)

@websocket_router.websocket('/discord/room/{room_id}')
async def join_discord_room(room_id: str, ws: WebSocket, user_id: str, db: Session = Depends(get_db)):
    try:
        user, room = join_room_discord_user(db, room_id, user_id)
        if user == None and room == None:
            return
        if not room.is_discord_room:
            return
        
        await core_websocket_func(ws, room, user_id, user.name)

    except Exception as e:
        print(e)
        exit_room_discord_user(db, user_id)
        del clients[room_id][user_id]
        del user_list[room_id][user_id]
        exit_user = {
            'event': 'exit_user',
            'user': class_to_json(user)
        }
        for client in clients[room_id].values():
            await client.send_json(exit_user)

async def core_websocket_func(ws: WebSocket, room: RoomSchema, user_id: str, name: str):
    await ws.accept()

    room_id = room.room_id

    my_info = create_default_user(user_id, name)
    join_new_user = class_to_json({
        'event': 'join_user', 
        'user': my_info
    })

    if not clients.get(room_id):
        clients[room_id] = {}
    my_room = clients.get(room_id)
    for client in my_room.values():
        await client.send_json(join_new_user)

    my_room[user_id] = ws
    

    my_room_user = user_list.get(room_id)
    if (my_room_user):
        my_room_user[user_id] = my_info
    else:
        user_list[room_id] = { user_id: my_info }
        my_room_user = user_list.get(room_id)
    
    init_info = class_to_json({
        'event': 'init_info', 
        'room': {
            "room_id": room_id,
            "expired_at": room.expired_at,
            "created_at": room.created_at,
            "users": list(my_room_user.values())
        },
        'user_id': user_id
    })
    await ws.send_json(init_info)

    while True:
        data: dict = await ws.receive_json()
        event_name = data.get('event')
        if not event_name:
            continue
        if not event_name in allow_event:
            continue

        if websocket_request_validator[event_name](data):
            websocket_funcs[event_name](room_id, user_id, data)
            data['user_id'] = user_id
            if event_name == 'reaction':
                wait_seconds = data['wait_seconds']
                threading.Thread(target=return_reaction, args=(room_id, data, wait_seconds)).start()
                del data['wait_seconds']
            for client in my_room.values():
                await client.send_json(data)

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

def return_reaction(room_id: str, data: dict, wait_seconds: int):
    time.sleep(wait_seconds)
    data['event'] = 'finish_reaction'

    my_room: dict = clients[room_id]
    for client in my_room.values():
        asyncio.run(client.send_json(data))
