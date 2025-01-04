import pytest

from pydantic_core import ValidationError
from sqlalchemy.future import select

from app.db.base import User
from app.enums.user import UserRole
from app.schemas.user import UserCreate, UserRead 


def test_user_create_schema_valid(default_user_data):
    user = UserCreate(**default_user_data)
    assert user.username == "defaultuser"
    assert user.password == "DefaultPassword1!"
    assert user.email == "defaultuser@example.com"


@pytest.mark.parametrize("invalid_username", ["t", "12", ""])
def test_user_create_schema_invalid_username(default_user_data, invalid_username):
    data = default_user_data.copy()
    data["username"] = invalid_username

    with pytest.raises(ValidationError) as exception:
        UserCreate(**data)

    assert "username" in str(exception.value)


@pytest.mark.parametrize("invalid_password", ["t", "12", "securepassword"])
def test_user_create_schema_invalid_password(default_user_data, invalid_password):
    data = default_user_data.copy()
    data["password"] = invalid_password

    with pytest.raises(ValidationError) as exception:
        UserCreate(**data)

    assert "password" in str(exception.value)


@pytest.mark.parametrize("invalid_email", ["t", "12", "some_email", "data.com", "@gmail.com", "email@abc"])
def test_user_create_schema_invalid_email(default_user_data, invalid_email):
    data = default_user_data.copy()
    data["email"] = invalid_email

    with pytest.raises(ValidationError) as exception:
        UserCreate(**data)

    assert "email" in str(exception.value)


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
    assert user_out.role == UserRole.USER


@pytest.mark.asyncio
async def test_user_creation(db_async):
    data = {
        "username": "testuser",
        "password": "SecurePassword1!",
        "email": "some_email@user.com"
    }

    new_user = User(**data)
    db_async.add(new_user)
    await db_async.commit()

    result = await db_async.execute(select(User).filter(User.username == "testuser"))
    user: User = result.scalars().first()

    assert user is not None
    assert user.username == "testuser"
    assert user.email == "some_email@user.com"
    assert user.role == UserRole.USER


@pytest.mark.asyncio
async def test_user_unique_constraints(db_async):

    data = {
        "username": "testuser",
        "password": "SecurePassword1!",
        "email": "unique_email@user.com"
    }

    user1 = User(**data)
    db_async.add(user1)
    await db_async.commit()

    duplicate_data = {
        "username": "testuser",
        "password": "SecurePassword1!",
        "email": "other_email@user.com"
    }

    user2 = User(**duplicate_data)

    db_async.add(user2)
    try:
        await db_async.commit()
        assert False, "Should not allow duplicate usernames"
    except Exception:
        await db_async.rollback()


@pytest.mark.asyncio
async def test_user_deletion(db_async):
    data = {
        "username": "testuser",
        "password": "SecurePassword1!",
        "email": "delete_me@user.com"
    }
    user = User(**data)
    db_async.add(user)
    await db_async.commit()

    result = await db_async.execute(select(User).filter(User.username == "testuser"))
    user_to_delete: User = result.scalars().first()
    await db_async.delete(user_to_delete)
    await db_async.commit()

    result = await db_async.execute(select(User).filter(User.username == "testuser"))
    deleted_user: User = result.scalars().first()
    assert deleted_user is None


@pytest.mark.asyncio
async def test_user_update(db_async):
    data = {
        "username": "testuser",
        "password": "SecurePassword1!",
        "email": "update_me@user.com"
    }
    user = User(**data)
    db_async.add(user)
    await db_async.commit()

    result = await db_async.execute(select(User).filter(User.username == "testuser"))
    user_to_update: User = result.scalars().first()
    user_to_update.email = "updated_email@user.com"
    await db_async.commit()

    result = await db_async.execute(select(User).filter(User.username == "testuser"))
    updated_user: User = result.scalars().first()
    assert updated_user.email == "updated_email@user.com"


@pytest.mark.asyncio
async def test_user_role_default(db_async):
    data = {
        "username": "testuser",
        "password": "SecurePassword1!",
        "email": "testrole@user.com"
    }
    user = User(**data)
    db_async.add(user)
    await db_async.commit()

    result = await db_async.execute(select(User).filter(User.username == "testuser"))
    user_from_db: User = result.scalars().first()
    assert user_from_db.role == UserRole.USER


@pytest.mark.asyncio
async def test_user_role_change(db_async):
    data = {
        "username": "adminuser",
        "password": "SecurePassword1!",
        "email": "admin@user.com"
    }
    user = User(**data)
    db_async.add(user)
    await db_async.commit()

    result = await db_async.execute(select(User).filter(User.username == "adminuser"))
    user_from_db: User = result.scalars().first()
    user_from_db.role = UserRole.ADMIN
    await db_async.commit()

    result = await db_async.execute(select(User).filter(User.username == "adminuser"))
    updated_user: User = result.scalars().first()
    assert updated_user.role == UserRole.ADMIN
