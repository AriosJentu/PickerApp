from fastapi import APIRouter
from app.api.v1.endpoints.auth import auth, account
from app.api.v1.endpoints.lobby import lobby
from app.api.v1.endpoints.users import users, admin


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(account.router, prefix="/account", tags=["account"])

api_router.include_router(lobby.router, prefix="/lobby", tags=["lobby"])

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
