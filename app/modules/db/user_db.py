from fastapi_users.db import SQLAlchemyUserDatabase
from app.modules.auth.user.models import User
from app.dependencies.database import SessionLocal


user_db = SQLAlchemyUserDatabase(SessionLocal, User)
