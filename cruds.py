from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import Tuple
from db.db import Session
from db.schemas import Room, User
from schemas import Room as RoomSchema, User as UserSchema
from websocket_funcs import clients, user_list
from utils import class_to_json, get_guild_and_vc_id, get_room_id_by_discord_info, generate_user_id

valid_limits = [12, 24, 36, 48]

def create_new_room(db: Session, limit: int) -> RoomSchema:
    if limit in valid_limits:
        valid_limit = limit
    else:
        valid_limit = 24

    room_orm = Room(
        expired_at = datetime.now() + timedelta(hours=valid_limit)
    )
    db.add(room_orm)
    db.commit()
    db.refresh(room_orm)
    return room_orm

def get_room_by_id(db: Session, room_id: str) -> RoomSchema:
    room_orm = db.query(Room).filter(Room.room_id.like(f'%{room_id}%')).first()
    if not room_orm:
        raise HTTPException(status_code=404, detail='this room is not exist')
    return RoomSchema.from_orm(room_orm)

def get_user_by_id(db: Session, user_id: str) -> RoomSchema:
    user_orm = db.query(User).filter(User.user_id.like(f'%{user_id}%')).first()
    if not user_orm:
        raise HTTPException(status_code=404, detail='this user is not exist')
    return UserSchema.from_orm(user_orm)

def join_room_by_id(db: Session, room_id: str, user_name: str) -> Tuple[UserSchema, RoomSchema]:
    room_orm = db.query(Room).filter(Room.room_id == room_id).first()
    if room_orm == None:
        return None, None
    room = RoomSchema.from_orm(room_orm)
    if room.expired_at < datetime.now():
        return None, None
    if len(room.users) >= 12:
        return None, None
    user_orm = User(
        room_id = room_id,
        name = user_name
    )
    db.add(user_orm)
    db.commit()
    db.refresh(user_orm)
    db.refresh(room_orm)
    user = UserSchema.from_orm(user_orm)
    room = RoomSchema.from_orm(room_orm)
    return user, room

def exit_room_by_id(db: Session, user_id: str) -> None:
    user_orm = db.query(User).filter(User.user_id == user_id).first()
    if user_orm is None:
        return
    db.delete(user_orm)
    db.commit()
    return

def delete_expired_rooms(db: Session) -> None:
    room_orms = db.query(Room).all()
    now = datetime.now()
    for room_orm in room_orms:
        if room_orm.expired_at < now:
            db.delete(room_orm)
    db.commit()

def create_new_room_on_discord(db: Session, guild_id: int, vc_id: int, limit: int) -> RoomSchema:
    room_id = get_room_id_by_discord_info(guild_id, vc_id)

    base_room_id = room_id[:room_id.rfind('-')]
    room_orm = db.query(Room).filter(Room.room_id.like(f'%{base_room_id}%')).first()
    print(room_orm)
    if room_orm:
        raise HTTPException(status_code=400, detail='this room is already exist')

    if limit in valid_limits:
        valid_limit = limit
    else:
        valid_limit = 24

    room_orm = Room(
        room_id = room_id,
        expired_at = datetime.now() + timedelta(hours=valid_limit),
        is_discord_room = True
    )
    db.add(room_orm)
    db.commit()
    db.refresh(room_orm)
    return room_orm

def create_discord_user(db: Session, room_id: str, user_id: int, name: str):
    room_orm = db.query(Room).get(room_id)
    if room_orm is None:
        raise HTTPException(status_code=404, detail='this room is not exist')
    if room_orm.expired_at < datetime.now():
        raise HTTPException(status_code=404, detail='this room is expired')

    str_user_id = str(hex(user_id))[2:]
    user_orm = db.query(User).filter(User.user_id.like(f'%{str_user_id}%')).first()
    if user_orm:
        raise HTTPException(status_code=400, detail='this user is already exist')

    
    guild_id, vc_id = get_guild_and_vc_id(room_id)

    user_orm = User(
        user_id = generate_user_id(user_id),
        name = name,
        discord_guild_id = guild_id,
        discord_vc_id = vc_id
    )

    db.add(user_orm)
    db.commit()
    user = UserSchema.from_orm(user_orm)
    return user


def delete_room_and_user_on_discord(db: Session, room_id: str) -> None:
    room_orm = db.query(Room).filter(Room.room_id == room_id).first()
    if room_orm is None:
        raise HTTPException(status_code=404, detail='room is not exist')
    db.delete(room_orm)

    guild_id, vc_id = get_guild_and_vc_id(room_id)

    user_orms = db.query(User).filter(User.discord_guild_id == guild_id, User.discord_vc_id == vc_id).all()
    for user_orm in user_orms:
        db.delete(user_orm)
    db.commit()

def join_room_discord_user(db: Session, room_id: str, user_id: str) -> Tuple[UserSchema, RoomSchema]:
    room_orm = db.query(Room).filter(Room.room_id == room_id).first()
    if room_orm == None:
        return None, None
    room = RoomSchema.from_orm(room_orm)
    if room.expired_at < datetime.now():
        return None, None
    if len(room.users) >= 12:
        return None, None
    
    user_orm = db.query(User).get(user_id)
    user_orm.room_id = room_id

    db.commit()
    db.refresh(user_orm)
    db.refresh(room_orm)
    user = UserSchema.from_orm(user_orm)
    room = RoomSchema.from_orm(room_orm)
    return user, room

def exit_room_discord_user(db: Session, user_id: str) -> None:
    user_orm = db.query(User).get(user_id)
    if user_orm is None:
        raise HTTPException(status_code=404, detail='user is not exist')
    user_orm.room_id = None

    db.commit()
    db.refresh(user_orm)
    return

async def exit_discord(db: Session, room_id: str, user_id: str) -> None:
    user_orm = db.query(User).get(user_id)
    if user_orm is None:
        raise HTTPException(status_code=404, detail='user is not exist')
    if user_orm.room_id is None:
        raise HTTPException(status_code=404, detail='user is not exist in room')
    user_orm.room_id = None
    db.commit()
    ws = clients[room_id][user_id]
    my_room = clients[room_id]
    disconnect_notify = {
        'event': 'websocket_disconnect'
    }
    await ws.send_json(disconnect_notify)
    del clients[room_id][user_id]
    del user_list[room_id][user_id]
    await ws.close()
    exit_user = {
        'event': 'exit_user',
        'user': class_to_json(UserSchema.from_orm(user_orm))
    }
    for client in my_room.values():
        await client.send_json(exit_user)
