from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.main import router
from db.db import engine
from db.schemas import Base

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title='EmoMee'
)

app.add_middleware(
	CORSMiddleware,
	allow_credentials=True,
	allow_origins=['*'],
	allow_methods=['*'],
	allow_headers=['*'],
)

app.include_router(router)
