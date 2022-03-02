from db.db import Session
from db.schema import Room, User
from schemas import Room as RoomSchema

def create_new_room(db: Session) -> RoomSchema:
    room_orm = Room()
    db.add(room_orm)
    db.commit()
    db.refresh(room_orm)
    return room_orm

def join_room_by_id(db: Session, room_id: str, user_name: str) -> RoomSchema:
    user_orm = User(
        room_id = room_id,
        name = user_name
    )
    db.add(user_orm)
    db.commit()
    room_orm = db.query(Room).filter(Room.room_id == room_id).first()
    return room_orm
