import datetime
from typing import Any
from sqlalchemy import Boolean, Column, DateTime, func
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer
from sqlalchemy.orm import relationship
from uuid import uuid4

@as_declarative()
class Base:
	id: Any
	__name__: Any

def generate_uuid():
	return str(uuid4())

class User(Base):
	__tablename__ = 'users'
	user_id = Column(String, primary_key=True, default=generate_uuid)
	room_id = Column(String, ForeignKey('rooms.room_id'), nullable=True)
	name = Column(String)
	discord_guild_id = Column(String)
	discord_vc_id = Column(String)

class Room(Base):
	__tablename__ = 'rooms'
	room_id = Column(String, primary_key=True, default=generate_uuid)
	is_discord_room = Column(Boolean, default=False)
	expired_at = Column(DateTime, default=func.now() + datetime.timedelta(days=1))
	created_at = Column(DateTime, default=func.now())

	users = relationship('User', foreign_keys='User.room_id')
