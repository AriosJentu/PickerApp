from fastapi_users.db import SQLAlchemyUserDatabase
from app.db.base import User
from app.db.session import SessionLocal


user_db = SQLAlchemyUserDatabase(SessionLocal, User)
