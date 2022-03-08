from fastapi import APIRouter, Depends
from cruds import create_new_room, get_room_by_id
from db.db import get_db
from db.db import Session
from schemas import CreateRoom, Room as RoomSchema

api_router = APIRouter()

@api_router.post('/room', response_model=RoomSchema)
async def create_room(payload: CreateRoom, db: Session = Depends(get_db)):
    room = create_new_room(db, payload.limit)
    return room

@api_router.get('/room/{room_id}', response_model=RoomSchema)
async def get_room(room_id: str, db: Session = Depends(get_db)):
    room = get_room_by_id(db, room_id)
    return room
