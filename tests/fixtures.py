from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pytest import fixture
from sqlalchemy.orm.session import Session
from cruds import create_new_room
from main import app
from db.db import get_db
from db.schemas import Base
import sqlalchemy_utils
import os

DATABASE = 'postgresql'
USER = os.environ.get('POSTGRES_USER')
PASSWORD = os.environ.get('POSTGRES_PASSWORD')
HOST = os.environ.get('POSTGRES_HOST')
DB_NAME = 'emomee_test'

DATABASE_URL = "{}://{}:{}@{}/{}".format(DATABASE, USER, PASSWORD, HOST, DB_NAME)

ECHO_LOG = False

client = TestClient(app)

engine = create_engine(DATABASE_URL, echo=ECHO_LOG)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@fixture(scope="function")
def use_test_db_fixture():
  """
  Override get_db with test DB
  get_db関数をテストDBで上書きする
  """
  if not sqlalchemy_utils.database_exists(DATABASE_URL):
    print('[INFO] CREATE DATABASE')
    sqlalchemy_utils.create_database(DATABASE_URL)

  Base.metadata.drop_all(engine)
  Base.metadata.create_all(engine)

  def override_get_db():
    try:
      db = SessionLocal()
      yield db
    finally:
      db.close()

  app.dependency_overrides[get_db] = override_get_db
  yield SessionLocal()

@fixture
def session_for_test():
  """
  DB Session for test
  """
  session = SessionLocal()
  yield session
  
  session.close()

@fixture
def room_for_test(
    session_for_test: Session,
    limit: int = 12
):
    """
    create room for test
    """
    r = create_new_room(session_for_test, limit)
    return r
