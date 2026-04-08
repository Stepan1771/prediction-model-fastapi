from .base import AppException


class UsernameAlreadyExistsError(AppException):
    status_code = 409
    code = "USERNAME_ALREADY_EXISTS"

    def __init__(self, username: str) -> None:
        super().__init__(f"Имя пользователя '{username}' уже используется")


class AuthenticationRequiredError(AppException):
    status_code = 401
    code = "AUTH_REQUIRED"
    detail = "Требуется аутентификация"


class InvalidCredentialsError(AppException):
    status_code = 403
    code = "INVALID_CREDENTIALS"
    detail = "Неверный логин или пароль"
