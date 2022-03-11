from fastapi import APIRouter, Depends
from cruds import create_discord_user, create_new_room, create_new_room_on_discord, delete_expired_rooms, delete_room_and_user_on_discord, exit_discord, get_room_by_id, get_user_by_id
from db.db import get_db
from db.db import Session
from schemas import CreateDiscordUser, CreateRoom, CreateRoomOnDiscord, DeleteResponse, Room as RoomSchema, User as UserSchema
from utils import get_room_id_by_discord_info

api_router = APIRouter()
discord_router = APIRouter()

@api_router.post('/room', response_model=RoomSchema)
async def create_room(payload: CreateRoom = None, db: Session = Depends(get_db)):
    room = create_new_room(db, payload.limit if payload is not None else CreateRoom(limit=24))
    return room

@api_router.get('/room/{room_id}', response_model=RoomSchema)
async def get_room(room_id: str, db: Session = Depends(get_db)):
    room = get_room_by_id(db, room_id)
    return room

@api_router.delete('/room/refresh', response_model=DeleteResponse)
async def refresh_rooms(db: Session = Depends(get_db)):
    delete_expired_rooms(db)
    return { 'status': 'OK' }

@api_router.get('/user/{user_id}', response_model=UserSchema)
async def get_user_info(user_id: str, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    return user

@discord_router.post('/room', response_model=RoomSchema)
async def create_room_on_discord(payload: CreateRoomOnDiscord, db: Session = Depends(get_db)):
    room = create_new_room_on_discord(db, payload.guild_id, payload.vc_id, payload.limit)
    return room

@discord_router.post('/room/{room_id}/user', response_model=UserSchema)
async def create_user_on_discord(room_id: str, payload: CreateDiscordUser, db: Session = Depends(get_db)):
    user = create_discord_user(db, room_id, payload.user_id, payload.name)
    return user

@discord_router.get('/room', response_model=RoomSchema)
async def get_room_by_discord_info(guild_id: int, vc_id: int, db: Session = Depends(get_db)):
    room_id = get_room_id_by_discord_info(guild_id, vc_id)
    room = get_room_by_id(db, room_id[:room_id.rfind('-')])
    return room

@discord_router.delete('/room/{room_id}/user/{user_id}', response_model=DeleteResponse)
async def exit_vc_channel(room_id: str, user_id: str, db: Session = Depends(get_db)):
    await exit_discord(db, room_id, user_id)
    return { 'status': 'OK' }
    
@discord_router.delete('/room/{room_id}', response_model=DeleteResponse)
async def close_room_on_discord(room_id: str, db: Session = Depends(get_db)):
    delete_room_and_user_on_discord(db, room_id)
    return { 'status': 'OK' }
    