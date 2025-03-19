import pytest

from typing import Optional

from pydantic_core import ValidationError
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.user.models import User
from app.modules.auth.user.enums import UserRole
from app.modules.auth.user.schemas import UserCreate, UserRead 
from tests.utils.types import InputData


@pytest.mark.parametrize(
    "user_data, is_valid, where",
    [
        ({"username": "validuser",   "email": "valid@example.com",    "password": "StrongPass1!"},     True,   ""),
        ({"username": "t",           "email": "valid@example.com",    "password": "StrongPass1!"},     False,  "username"),
        ({"username": "12",          "email": "valid@example.com",    "password": "StrongPass1!"},     False,  "username"),
        ({"username": "validuser",   "email": "invalid-email",        "password": "StrongPass1!"},     False,  "email"),
        ({"username": "validuser",   "email": "invalid-email@abcd",   "password": "StrongPass1!"},     False,  "email"),
        ({"username": "validuser",   "email": "abcd.com",             "password": "StrongPass1!"},     False,  "email"),
        ({"username": "validuser",   "email": "@abcd.com",            "password": "StrongPass1!"},     False,  "email"),
        ({"username": "validuser",   "email": "valid@example.com",    "password": "123"},              False,  "password"),
        ({"username": "validuser",   "email": "valid@example.com",    "password": "strongpassword"},   False,  "password"),
        ({"username": "validuser",   "email": "valid@example.com",    "password": "strongpasswd123"},  False,  "password"),
    ]
)
def test_user_create_schema_valid(
        user_data: InputData, 
        is_valid: bool, 
        where: str
):


    if is_valid:
        user = UserCreate(**user_data)
        assert user.username == user_data["username"]
        assert user.email == user_data["email"]
        assert user.password == user_data["password"]
    else:
        with pytest.raises(ValidationError) as exception:
            UserCreate(**user_data)
        
        assert where in str(exception.value)


@pytest.mark.parametrize(
    "user_data, is_valid, where",
    [
        ({"id": 1,      "username": "testuser",     "email": "some_email@example.com",  "role": UserRole.USER},      True,   ""),
        ({"id": 1,      "username": "testuser",     "email": "some_email@example.com",  "role": UserRole.MODERATOR}, True,   ""),
        ({"id": "1",    "username": "testuser",     "email": "some_email@example.com",  "role": UserRole.USER},      True,   ""),
        ({"id": -1,     "username": "testuser",     "email": "some_email@example.com",  "role": 2},                  True,   ""),
        ({"id": 1,      "username": "testuser",     "email": "some_email@example.com",  "role": "1"},                True,   ""),
        ({"id": 1,      "username": "12",           "email": "123@123",                 "role": UserRole.USER},      False,  "email"),
        ({"id": 1,      "username": "12",           "email": "123@123",                 "role": 0},                  False,  "role"),
        ({"id": 123,    "username": "12",           "email": "123@123",                 "role": -1},                 False,  "role"),
        ({"id": 0,      "username": "testuser",     "email": "some_email@example.com",  "role": "user"},             False,  "role"),
    ]
)
def test_user_out_schema(
        user_data: InputData, 
        is_valid: bool, 
        where: str
):

    if is_valid:
        user_out = UserRead(**user_data)
        assert user_out.id == int(user_data["id"])
        assert user_out.username == user_data["username"]
        assert user_out.email == user_data["email"]
        assert user_out.role == int(user_data["role"])
    else:
        with pytest.raises(ValidationError) as exception:
            UserRead(**user_data)
        
        assert where in str(exception.value)


@pytest.mark.parametrize(
    "user_data, expected_error",
    [
        ({"username": "testuser",   "password": "SecurePassword1!", "email": "some_email@user.com"},    None),
        ({"username": "testuser",   "password": "SecurePassword1!", "email": "another_email@user.com"}, None),  
        ({"username": "newuser",    "password": "SecurePassword1!", "email": "invalid_email"},          None),
        ({"username": "newuser",    "password": "123",              "email": "new_email@user.com"},     None),
    ],
)
@pytest.mark.asyncio
async def test_user_creation(
        db_async: AsyncSession, 
        user_data: InputData, 
        expected_error: Optional[str]
):

    if expected_error is None:
        
        new_user = User(**user_data)
        db_async.add(new_user)
        await db_async.commit()

        result = await db_async.execute(select(User).filter(User.username == user_data["username"]))
        user: User = result.scalars().first()

        assert user is not None
        assert user.username == user_data["username"]
        assert user.email == user_data["email"]
        assert user.role == UserRole.USER

    else:

        try:
            new_user = User(**user_data)
            db_async.add(new_user)
            await db_async.commit()

        except Exception as e:
            assert expected_error in str(e)

        else:
            pytest.fail(f"Expected error '{expected_error}' but no error occurred.")


@pytest.mark.parametrize(
    "user_data_original, user_data_duplicate, where",
    [
        (
            {"username": "testuser",    "password": "SecurePassword1!",     "email": "unique_email@user.com"},
            {"username": "testuser",    "password": "SecurePassword1!",     "email": "other_email@user.com"},
            "username",
        ),
        (
            {"username": "uniqueuser",  "password": "SecurePassword1!",     "email": "unique_email@user.com"},
            {"username": "otheruser",   "password": "SecurePassword1!",     "email": "unique_email@user.com"},
            "email",
        ),
    ],
)
@pytest.mark.asyncio
async def test_user_unique_constraints(
        db_async: AsyncSession, 
        user_data_original: InputData, 
        user_data_duplicate: InputData, 
        where: str
):

    user1 = User(**user_data_original)
    db_async.add(user1)
    await db_async.commit()

    user2 = User(**user_data_duplicate)
    db_async.add(user2)

    with pytest.raises(IntegrityError) as exc_info:
        await db_async.commit()

    assert where in str(exc_info.value)
    await db_async.rollback()


@pytest.mark.parametrize(
    "user_data, delete_username, expected_deleted",
    [
        (
            {"username": "testuser", "password": "SecurePassword1!", "email": "delete_me@user.com"},
            "testuser",
            True,
        ),
        (
            {"username": "testuser", "password": "SecurePassword1!", "email": "delete_me@user.com"},
            "nonexistentuser",
            False,
        ),
    ],
)
@pytest.mark.asyncio
async def test_user_deletion(
        db_async: AsyncSession, 
        user_data: InputData, 
        delete_username: str, 
        expected_deleted: bool
):

    user = User(**user_data)
    db_async.add(user)
    await db_async.commit()

    try:
        result = await db_async.execute(select(User).filter(User.username == delete_username))
        user_to_delete: User = result.scalars().first()

        if user_to_delete:
            await db_async.delete(user_to_delete)
            await db_async.commit()
        else:
            assert not expected_deleted, "Expected no deletion, but user was found"

    except NoResultFound:
        assert not expected_deleted, "Expected no deletion, but an exception occurred"

    result = await db_async.execute(select(User).filter(User.username == "testuser"))
    deleted_user: User = result.scalars().first()

    if expected_deleted:
        assert deleted_user is None, "User was not deleted as expected"
    else:
        assert deleted_user is not None, "User was unexpectedly deleted"


@pytest.mark.parametrize(
    "initial_data, update_data, expected_username, expected_email",
    [
        (
            {"username": "testuser", "password": "SecurePassword1!", "email": "update_me@user.com"},
            {"email": "updated_email@user.com"},
            "testuser", "updated_email@user.com",
        ),
        (
            {"username": "testuser", "password": "SecurePassword1!", "email": "update_me@user.com"},
            {"username": "new_username"},
            "new_username", "update_me@user.com",
        ),
        (
            None,
            {"email": "updated_email@user.com"},
            None, None,
        ),
    ],
)
@pytest.mark.asyncio
async def test_user_update(
        db_async: AsyncSession, 
        initial_data: InputData, 
        update_data: InputData, 
        expected_username: str, 
        expected_email: str
):
    
    if initial_data:
        user = User(**initial_data)
        db_async.add(user)
        await db_async.commit()

    comparison_username = initial_data["username"] if initial_data else "nonexistentuser"
    try:
        result = await db_async.execute(select(User).filter(User.username == comparison_username))
        user_to_update: User = result.scalars().first()

        if user_to_update:
            for key, value in update_data.items():
                setattr(user_to_update, key, value)
            await db_async.commit()
        else:
            assert expected_username is None and expected_email is None, "Expected no update, but user was found"

    except NoResultFound:
        assert expected_email is None, "Expected no update, but an exception occurred"

    updated_username = update_data.get("username") or comparison_username
    result = await db_async.execute(select(User).filter(User.username == updated_username))
    updated_user: User = result.scalars().first()

    if expected_email is not None:
        assert updated_user is not None, "User was not found after update"
        assert updated_user.username == expected_username, f"Username was not updated correctly: {updated_user.username}"
        assert updated_user.email == expected_email, f"Email was not updated correctly: {updated_user.email}"
    else:
        assert updated_user is None, "User should not exist"


@pytest.mark.parametrize(
    "input_data, expected_role",
    [
        (
            {"username": "testuser",        "password": "SecurePassword1!",     "email": "testrole@user.com"},
            UserRole.USER,
        ),
        (
            {"username": "moderatoruser",   "password": "SecurePassword1!",     "email": "moderator@user.com",  "role": UserRole.MODERATOR},
            UserRole.MODERATOR,
        ),
        (
            {"username": "adminuser",       "password": "SecurePassword1!",     "email": "admin@user.com",      "role": UserRole.ADMIN},
            UserRole.ADMIN,
        ),
    ],
)
@pytest.mark.asyncio
async def test_user_role_assignment(
        db_async: AsyncSession, 
        input_data: InputData, 
        expected_role: UserRole
):
    
    user = User(**input_data)
    db_async.add(user)
    await db_async.commit()

    result = await db_async.execute(select(User).filter(User.username == input_data["username"]))
    user_from_db: User = result.scalars().first()

    assert user_from_db is not None, "User was not found in the database"
    assert user_from_db.role == expected_role, f"Expected role {expected_role}, but got {user_from_db.role}"


@pytest.mark.parametrize(
    "initial_role, new_role",
    [
        (UserRole.USER,         UserRole.MODERATOR),
        (UserRole.USER,         UserRole.ADMIN),
        (UserRole.MODERATOR,    UserRole.USER),
        (UserRole.MODERATOR,    UserRole.ADMIN),
        (UserRole.ADMIN,        UserRole.USER),
        (UserRole.ADMIN,        UserRole.MODERATOR),
        (UserRole.USER,         UserRole.USER),
        (UserRole.MODERATOR,    UserRole.MODERATOR),
        (UserRole.ADMIN,        UserRole.ADMIN),
    ],
)
@pytest.mark.asyncio
async def test_user_role_change(
        db_async: AsyncSession, 
        initial_role: UserRole, 
        new_role: UserRole
):
    
    data = {
        "username": "someuser",
        "password": "SecurePassword1!",
        "email": "admin@user.com",
        "role": initial_role,
    }
    user = User(**data)
    db_async.add(user)
    await db_async.commit()

    result = await db_async.execute(select(User).filter(User.username == "someuser"))
    user_from_db: User = result.scalars().first()
    assert user_from_db.role == initial_role, f"Expected initial role {initial_role}, but got {user_from_db.role}"

    user_from_db.role = new_role
    await db_async.commit()

    result = await db_async.execute(select(User).filter(User.username == "someuser"))
    updated_user: User = result.scalars().first()
    assert updated_user.role == new_role, f"Expected updated role {new_role}, but got {updated_user.role}"
