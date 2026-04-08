from typing import Annotated

from fastapi import Depends

from .user import get_user_repository

from repositories import UserRepository

from services import AuthService


def get_auth_service(
        user_repository: Annotated[
            UserRepository,
            Depends(get_user_repository),
        ],
) -> AuthService:
    return AuthService(user_repository=user_repository)


