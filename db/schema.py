import datetime
from typing import Any
from sqlalchemy import Boolean, Column, DateTime, func, event
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

class Emoji(Base):
	__tablename__ = 'emojis'
	user_id = Column(String, ForeignKey('users.user_id'), primary_key=True)
	emotion_id = Column(Integer, ForeignKey('emotions.emotion_id'), primary_key=True)
	name = Column(String, nullable=True)

	user = relationship('User')
	emotion = relationship('Emotion')

class User(Base):
	__tablename__ = 'users'
	user_id = Column(String, primary_key=True, default=generate_uuid)
	room_id = Column(String, ForeignKey('rooms.room_id'))
	name = Column(String)
	emotion_id = Column(Integer, ForeignKey('emotions.emotion_id'), default=1)
	is_afk = Column(Boolean, default=False)

	emotion = relationship('Emotion', backref='having_users')

	# emotions = relationship('Emotion', secondary=Emoji.__tablename__, back_populates='users')
	# emojis = relationship('Emoji')

class Emotion(Base):
	__tablename__ = 'emotions'
	emotion_id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String, unique=True)

	# users = relationship('User', secondary=Emoji.__tablename__, back_populates='emotions')
	# emojis = relationship('Emoji')

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

@event.listens_for(Emotion.__table__, 'after_create')
def insert_data(target, connection, **kw):
	connection.execute(target.insert(),
		{'name':'neutral'},
		{'name':'happy'},
		{'name':'sad'},
		{'name':'angry'},
		{'name':'fearful'},
		{'name':'disgusted'},
		{'name':'surprised'},
	)
