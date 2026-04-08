from sqlalchemy.exc import IntegrityError

from core.security import hash_password

from exceptions import UsernameAlreadyExistsError

from repositories import UserRepository

from schemas import (
    RegisterRequest,
    UserCreate,
)

from core.logging import logger


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
    ) -> None:
        self.user_repository = user_repository

    async def _check_username_unique(self, username: str) -> None:
        user = await self.user_repository.get_by_username(username=username)
        if user:
            logger.info(f"Пользователь с именем <{username}> уже существует")
            raise UsernameAlreadyExistsError(username=username)

    async def register(
            self,
            schema: RegisterRequest,
    ) -> UserCreate:
        logger.info(f"Регистрация пользователя с именем <{schema.username}>")

        await self._check_username_unique(username=schema.username)

        password = hash_password(password=schema.password)

        try:
            user = await self.user_repository.create(
                schema=UserCreate(
                    **schema.model_dump(exclude={"password"}),
                    password_hash=password,
                ),
            )

            return user

        except IntegrityError:
            logger.warning(f"Race condition при регистрации пользователя <{schema.username}>")
            raise UsernameAlreadyExistsError(username=schema.username)

