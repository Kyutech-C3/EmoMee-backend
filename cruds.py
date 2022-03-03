from typing import Tuple
from db.db import Session
from db.schema import Room, User
from schemas import Room as RoomSchema, User as UserSchema

def create_new_room(db: Session) -> RoomSchema:
    room_orm = Room()
    db.add(room_orm)
    db.commit()
    db.refresh(room_orm)
    return room_orm

def join_room_by_id(db: Session, room_id: str, user_name: str) -> Tuple[UserSchema, RoomSchema]:
    user_orm = User(
        room_id = room_id,
        name = user_name
    )
    db.add(user_orm)
    db.commit()
    db.refresh(user_orm)
    room_orm = db.query(Room).filter(Room.room_id == room_id).first()
    user = UserSchema.from_orm(user_orm)
    room = RoomSchema.from_orm(room_orm)
    return user, room

def exit_room_by_id(db: Session, user_id: str) -> None:
    user_orm = db.query(User).filter(User.user_id == user_id).first()
    db.delete(user_orm)
    db.commit()
    return
