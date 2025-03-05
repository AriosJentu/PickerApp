import pytest

from app.db.base import User, Algorithm, Lobby, Team
from app.enums.user import UserRole

from tests.factories.user_factory import UserFactory
from tests.factories.token_factory import TokenFactory
from tests.factories.lobby_factory import LobbyFactory
from tests.factories.team_factory import TeamFactory
from tests.factories.algorithm_factory import AlgorithmFactory

from tests.types import (
    InputData,
    RouteBaseFixture,
    BaseObjectFixtureCallable,
    BaseAdditionalUserFixtureCallable,
    BaseUserFixture,
    BaseUserFixtureTokens,
    BaseUserFixtureCallable,
    BaseCreatorUsersFixture,
    BaseCreatorUsersFixtureCallable,
    BaseCreatorAdditionalUsersFixture,
    BaseCreatorAdditionalUsersFixtureCallable,
)
from tests.utils.user_utils import create_user_with_tokens


@pytest.fixture
def protected_route(request) -> RouteBaseFixture:
    return request.param


@pytest.fixture
def test_base_user_from_role(
        user_factory: UserFactory,
        token_factory: TokenFactory
) -> BaseUserFixtureCallable:
    
    async def test_base_user(
            role: UserRole = UserRole.USER,
            with_tokens: bool = False,
            is_refresh_token: bool = False
    ) -> BaseUserFixture | BaseUserFixtureTokens:
        user, access_token, refresh_token = await create_user_with_tokens(user_factory, token_factory, role)
        headers = {"Authorization": f"Bearer {refresh_token if is_refresh_token else access_token}"}

        if with_tokens:
            return user, access_token, refresh_token, headers

        return user, headers
    
    return test_base_user


@pytest.fixture
def test_base_creator_users_from_role(
        user_factory: UserFactory,
        token_factory: TokenFactory
) -> BaseCreatorUsersFixtureCallable:
    
    async def test_base_creator_users(role: UserRole = UserRole.USER) -> BaseCreatorUsersFixture:
        user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
        creator, creator_access_token, _ = await create_user_with_tokens(user_factory, token_factory, prefix="creator_user")
        headers = {"Authorization": f"Bearer {access_token}"}
        headers_creator = {"Authorization": f"Bearer {creator_access_token}"}

        return user, headers, creator, headers_creator
    
    return test_base_creator_users


@pytest.fixture
def test_base_creator_additional_users_from_role(
        user_factory: UserFactory,
        token_factory: TokenFactory
) -> BaseCreatorAdditionalUsersFixtureCallable:
    
    async def test_base_creator_additional_users(role: UserRole = UserRole.USER) -> BaseCreatorAdditionalUsersFixture:
        user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role=role)
        creator, creator_access_token, _ = await create_user_with_tokens(user_factory, token_factory, prefix="creator_user")
        user_to_add, additional_access_token, _ = await create_user_with_tokens(user_factory, token_factory, prefix="user_to_add")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        headers_creator = {"Authorization": f"Bearer {creator_access_token}"}
        headers_additional = {"Authorization": f"Bearer {additional_access_token}"}

        return user, headers, creator, headers_creator, user_to_add, headers_additional
    
    return test_base_creator_additional_users


@pytest.fixture
def test_add_extra_users_with_email_password(
        user_factory: UserFactory
) -> BaseAdditionalUserFixtureCallable:
    
    async def test_add_extra_users(
            update_data: InputData,
            is_duplicate_email: bool = False,
            is_duplicate_username: bool = False,
            is_failed: bool = False
    ) -> User | None:
        
        if is_failed:
            return
        
        default_data = {
            "username": "someusername_extra",
            "email":    "somemail_extra@example.com",
            "password": "SecurePassword1!",
            "role":     UserRole.USER
        }

        if is_duplicate_email:
            default_data["email"] = update_data["email"]

        if is_duplicate_username:
            default_data["username"] = update_data["username"]

        return await user_factory.create_from_data(default_data)
    
    return test_add_extra_users


@pytest.fixture
def test_create_algorithm_from_data(algorithm_factory: AlgorithmFactory) -> BaseObjectFixtureCallable:

    async def create_algorithm(user: User, is_algorithm_exists: bool = True) -> tuple[int, Algorithm]:
        if not is_algorithm_exists:
            return -1, None
        
        algorithm = await algorithm_factory.create(user)
        return algorithm.id, algorithm
    
    return create_algorithm


@pytest.fixture
def test_create_lobby_from_data(
        lobby_factory: LobbyFactory,
        test_algorithm: Algorithm
) -> BaseObjectFixtureCallable:

    async def create_lobby(user: User, is_lobby_exists: bool = True) -> tuple[int, Lobby]:
        if not is_lobby_exists:
            return -1, None
        
        lobby = await lobby_factory.create(user, test_algorithm)
        return lobby.id, lobby
    
    return create_lobby


@pytest.fixture
def test_create_team_from_data(
        team_factory: TeamFactory,
) -> BaseObjectFixtureCallable:

    async def create_team(lobby: Lobby, is_team_exists: bool = True) -> tuple[int, Team]:
        if not is_team_exists:
            return -1, None
        
        team = await team_factory.create(lobby)
        return team.id, team
    
    return create_team
