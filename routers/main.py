from fastapi import APIRouter
from .api import api_router, discord_router
from .websocket import websocket_router

router = APIRouter()

api_router.include_router(discord_router, prefix='/discord', tags=['discord'])
router.include_router(api_router, prefix='/api/v1')
router.include_router(websocket_router, prefix='/ws')
