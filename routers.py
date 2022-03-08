from datetime import datetime
import json
from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket
from cruds import create_new_room, exit_room_by_id, get_room_by_id, join_room_by_id
from db.db import get_db
from db.db import Session
from schemas import CreateRoom, Room as RoomSchema
from utils import class_to_json

emotion_list = [
    'neutral',
    'happy',
    'sad',
    'angry',
    'fearful',
    'disgusted',
    'surprised'
]

router = APIRouter()

clients = {}
user_list = {}

@router.post('/api/v1/room', response_model=RoomSchema)
async def create_room(payload: CreateRoom, db: Session = Depends(get_db)):
    room = create_new_room(db, payload.limit)
    return room

@router.get('/api/v1/room/{room_id}', response_model=RoomSchema)
async def get_room(room_id: str, db: Session = Depends(get_db)):
    room = get_room_by_id(db, room_id)
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

        my_info = {
            'user_id': user.user_id,
            'name': user.name,
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

        my_room_user = user_list.get(room.room_id)
        if (my_room_user):
            my_room_user[user.user_id] = my_info
        else:
            user_list[room.room_id] = { user.user_id: my_info }
            my_room_user = user_list.get(room.room_id)

        room_info = {
            "room_id": room.room_id,
            "expired_at": room.expired_at,
            "created_at": room.created_at,
            "users": list(user_list[room.room_id].values())
        }

        await ws.send_json(json.loads(json.dumps({
            'event': 'room_info',
            'room': room_info
        }, default=json_serial)))
        for client in my_room.values():
            await client.send_json(json.loads(json.dumps({'event': 'join_new_user', 'user': my_room_user[user.user_id]}, default=json_serial)))

        while True:
            data: dict = await ws.receive_json()
            if not data.get('event'):
                continue

            event_name = data.get('event')
            if data.keys() == {'event', 'emotion'} and event_name == 'change_emotion':
                changed_user = change_emotion(room_id, user.user_id, data.get('emotion'))
                if changed_user:
                    for client in my_room.values():
                        await client.send_json(json.loads(json.dumps({'event': 'changed_user', 'changed_user': changed_user}, default=json_serial)))

            if data.keys() == {'event', 'emotion', 'emoji'} and event_name == 'change_setting_emoji':
                changed_user = change_setting_emoji(room_id, user.user_id, data.get('emotion'), data.get('emoji'))
                if changed_user:
                    for client in my_room.values():
                        await client.send_json(json.loads(json.dumps({'event': 'changed_user', 'changed_user': changed_user}, default=json_serial)))

            if data.keys() == {'event', 'is_afk'} and event_name == 'switch_afk':
                changed_user = switch_afk(room_id, user.user_id, data.get('is_afk'))
                if changed_user:
                    for client in my_room.values():
                        await client.send_json(json.loads(json.dumps({'event': 'changed_user', 'changed_user': changed_user}, default=json_serial)))

            if data.keys() == {'event', 'is_speaking'} and event_name == 'switch_speaking':
                changed_user = switch_speaking(room_id, user.user_id, data.get('is_speaking'))
                if changed_user:
                    for client in my_room.values():
                        await client.send_json(json.loads(json.dumps({'event': 'changed_user', 'changed_user': changed_user}, default=json_serial)))

            if data.keys() == {'event', 'reaction', 'is_animation'} and event_name == 'reaction':
                if type(data.get('event')) is str and type(data.get('reaction')) is str and type(data.get('is_animation')) is bool:
                    data['user_id'] = user.user_id
                    for client in my_room.values():
                        await client.send_json(data)

    except Exception as e:
        print(e)
        exit_room_by_id(db, user.user_id)
        del clients[room.room_id][key]
        del user_list[room.room_id][user.user_id]
        for client in my_room.values():
            await client.send_json({'event': 'exit_user', 'user': class_to_json(user)})

def change_emotion(room_id: str, user_id: str, emotion: str):
    if emotion in emotion_list and user_list[room_id][user_id]['emotion'] != emotion:
        user_list[room_id][user_id]['emotion'] = emotion
        return user_list[room_id][user_id]

def change_setting_emoji(room_id: str, user_id: str, emotion: str, emoji: int):
    if emotion in emotion_list and user_list[room_id][user_id]['emoji'][emotion] != emoji:
        user_list[room_id][user_id]['emoji'][emotion] = emoji
        return user_list[room_id][user_id]

def switch_afk(room_id: str, user_id: str, is_afk: bool):
    if user_list[room_id][user_id]['is_afk'] != is_afk:
        user_list[room_id][user_id]['is_afk'] = is_afk
        return user_list[room_id][user_id]

def switch_speaking(room_id: str, user_id: str, is_speaking: bool):
    if user_list[room_id][user_id]['is_speaking'] != is_speaking:
        user_list[room_id][user_id]['is_speaking'] = is_speaking
        return user_list[room_id][user_id]

def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))
