from fastapi import APIRouter
from .api import api_router
from .websocket import websocket_router

router = APIRouter()

router.include_router(api_router, prefix='/api/v1')
router.include_router(websocket_router, prefix='/ws')
