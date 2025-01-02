from fastapi import APIRouter
from app.api.v1.endpoints import account, admin, auth, lobby, pick_ban, users


api_router = APIRouter()

api_router.include_router(account.router, prefix="/account", tags=["account"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(lobby.router, prefix="/lobby", tags=["lobby"])
api_router.include_router(pick_ban.router, prefix="/pick-ban", tags=["pick-ban"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
