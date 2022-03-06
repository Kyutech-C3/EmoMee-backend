from datetime import datetime, timedelta
from typing import Tuple
from db.db import Session
from db.schema import Emoji, Emotion, Room, User
from schemas import Room as RoomSchema, User as UserSchema

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

def join_room_by_id(db: Session, room_id: str, user_name: str) -> Tuple[UserSchema, RoomSchema]:
    room_orm = db.query(Room).filter(Room.room_id == room_id).first()
    if room_orm == None:
        return None, None
    room = RoomSchema.from_orm(room_orm)
    if room.expired_at < datetime.now():
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
    db.delete(user_orm)
    db.commit()
    return

def change_emotion(db: Session, user_id: str, emotion: str) -> UserSchema:
    user_orm = db.query(User).get(user_id)
    if user_orm == None:
        return
    emotion_orm = db.query(Emotion).filter(Emotion.name == emotion).first()
    if emotion_orm == None:
        return
    user_orm.emotion_id = emotion_orm.emotion_id
    db.commit()
    db.refresh(user_orm)
    user = UserSchema.from_orm(user_orm)
    return user

def change_setting_emoji(db: Session, user_id: str, emotion: str, emoji: str) -> UserSchema:
    user_orm = db.query(User).get(user_id)
    if user_orm == None:
        return

    emotion_orm = db.query(Emotion).filter(Emotion.name == emotion).first()

    emoji_orm = Emoji(
        user_id = user_id,
        emotion_id = emotion_orm.emotion_id,
        name = emoji
    )
    
    db.add(emoji_orm)
    db.commit()
    db.refresh(user_orm)
    user = UserSchema.from_orm(user_orm)
    return user

def switch_afk(db: Session, user_id: str, is_afk: bool) -> UserSchema:
    user_orm = db.query(User).get(user_id)
    if user_orm == None:
        return
    user_orm.is_afk = is_afk
    db.commit()
    db.refresh(user_orm)
    user = UserSchema.from_orm(user_orm)
    return user
