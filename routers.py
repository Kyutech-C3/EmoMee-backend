from fastapi import APIRouter, Depends, Request
from cruds import create_new_room, join_room_by_id
from db.db import get_db
from db.db import Session
from schemas import JoinUser, Room as RoomSchema

router = APIRouter()

@router.post('/room', response_model=RoomSchema)
async def create_room(db: Session = Depends(get_db)):
    room = create_new_room(db)
    return room

@router.post('/room/{room_id}', response_model=RoomSchema)
async def join_room(request: Request, room_id: str, payload: JoinUser, db: Session = Depends(get_db)):
    room = join_room_by_id(db, room_id, payload.name)
    return room
