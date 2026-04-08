from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBasicCredentials

from .user import get_user_repository

from core.security import (
    security,
    verify_password,
)

from exceptions import (
    AuthenticationRequiredError,
    InvalidCredentialsError,
)

from models import User

from repositories import UserRepository


async def get_current_user(
    credentials: Annotated[
        HTTPBasicCredentials | None,
        Depends(security),
    ],
    user_repository: Annotated[
        UserRepository,
        Depends(get_user_repository),
    ],
) -> User:
    if credentials is None:
        raise AuthenticationRequiredError()

    user = await user_repository.get_by_username(username=credentials.username)

    if not user or not verify_password(
            plain_password=credentials.password,
            hashed_password=user.password_hash,
    ):
        raise InvalidCredentialsError()

    return user