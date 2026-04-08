from pydantic import (
    BaseModel,
    ConfigDict,
)


class RegisterRequest(BaseModel):
    username: str
    password: str


class RegisterResponse(BaseModel):
    message: str
    user: str

    model_config = ConfigDict(
        from_attributes=True,
    )