from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import Tuple
from db.db import Session
from db.schema import Room, User
from schemas import Room as RoomSchema, User as UserSchema
import decimal

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
    room_orm = db.query(Room).filter(Room.room_id == room_id).first()
    if room_orm == None:
        raise HTTPException(status_code=400, detail='this room is not exist')
    return RoomSchema.from_orm(room_orm)

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
    room_orms = db.query(Room).filter(Room.is_discord_room == False).all()
    now = datetime.now()
    for room_orm in room_orms:
        if room_orm.expired_at < now:
            db.delete(room_orm)
    db.commit()

def create_new_room_on_discord(db: Session, guild_id: int, vc_id: int, limit: int) -> RoomSchema:
    room_id = f'{guild_id*7}-{vc_id*11}'

    room_orm = db.query(Room).get(room_id)
    if room_orm is not None:
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

    str_user_id = str(user_id)
    user_orm = db.query(User).get(str_user_id)
    if user_orm is not None:
        raise HTTPException(status_code=400, detail='this user is already exist')

    
    guild_id, vc_id = get_guild_and_vc_id(room_id)

    user_orm = User(
        user_id = str_user_id,
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
    db.delete(room_orm)

    guild_id, vc_id = get_guild_and_vc_id(room_id)

    user_orms = db.query(User).filter(User.discord_guild_id == guild_id, User.discord_vc_id == vc_id).all()
    for user_orm in user_orms:
        db.delete(user_orm)
    db.commit()

def get_guild_and_vc_id(room_id: str) -> Tuple[str, str]:
    discord_info = room_id.split('-')
    guild_id = decimal.Decimal(int(discord_info[0]))
    vc_id = decimal.Decimal(int(discord_info[1]))

    guild_id /= decimal.Decimal(7)
    vc_id /= decimal.Decimal(11)
    
    return str(int(guild_id)), str(int(vc_id))
    