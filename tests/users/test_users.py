from app.db.base import User
from app.enums.user import UserRole
from app.schemas.user import UserCreate, UserRead 


def test_user_creation(db):
    data = {
        "username": "testuser",
        "password": "securepassword",
        "email": "some_email@user.com"
    }

    new_user = User(**data)
    db.add(new_user)
    db.commit()

    user = db.query(User).filter(User.username == "testuser").first()
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "some_email@user.com"
    assert user.role == UserRole.USER


def test_user_create_schema_valid():
    data = {
        "username": "testuser",
        "password": "securepassword",
        "email": "some_email@user.com"
    }
    user = UserCreate(**data)
    assert user.username == "testuser"
    assert user.password == "securepassword"
    assert user.email == "some_email@user.com"


def test_user_out_schema():
    
    data = {
        "id": 1,
        "username": "testuser",
        "email": "testuser@email.com",
        "role": UserRole.USER
    }

    user_out = UserRead(**data)

    assert user_out.id == 1
    assert user_out.username == "testuser"
    assert user_out.email == "testuser@email.com"
    assert user_out.role == "user"
