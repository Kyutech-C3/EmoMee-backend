from datetime import datetime
from typing import List
from pydantic import BaseModel

class User(BaseModel):
    user_id: str
    name: str

    class Config:
        orm_mode = True

class CreateRoom(BaseModel):
    limit: int

class Room(BaseModel):
    room_id: str
    expired_at: datetime
    created_at: datetime
    users: List[User]

    class Config:
        orm_mode = True
