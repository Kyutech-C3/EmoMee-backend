import datetime
from typing import Any
from sqlalchemy import Column, DateTime, func
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
	room_id = Column(String, ForeignKey('rooms.room_id'))
	name = Column(String)

class DiscordUser(User):
	__tablename__ = 'discord_users'
	user_id = Column(String, ForeignKey('users.user_id'), primary_key=True)
	discord_user_id = Column(Integer)
	discord_guild_id = Column(Integer)
	discord_vc_id = Column(Integer)

class Room(Base):
	__tablename__ = 'rooms'
	room_id = Column(String, primary_key=True, default=generate_uuid)
	expired_at = Column(DateTime, default=func.now() + datetime.timedelta(days=1))
	created_at = Column(DateTime, default=func.now())
	users = relationship('User', foreign_keys='User.room_id')
