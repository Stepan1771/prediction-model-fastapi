from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)
from starlette import status

from core.config import settings

from api.depends import (
    get_current_user,
    get_auth_service,
)

from models import User

from schemas import (
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)

from services import AuthService


router = APIRouter(
    prefix=settings.api.v1.auth,
    tags=["Auth"],
)


@router.post(
    path="/register",
    summary="Регистрация нового пользователя",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
        service: Annotated[
            AuthService,
            Depends(get_auth_service),
        ],
        schema: RegisterRequest,
) -> RegisterResponse:
    user = await service.register(schema=schema)
    return RegisterResponse(
        message="Пользователь успешно зарегистрирован",
        user=user.username,
    )


@router.get(
    path="/me",
    summary="Получение информации о текущем пользователе",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def read_current_user(
        user: Annotated[
            User,
            Depends(get_current_user),
        ],
) -> UserResponse:
    return UserResponse(username=user.username)
