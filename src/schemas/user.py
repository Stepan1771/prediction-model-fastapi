from pydantic import (
    BaseModel,
    ConfigDict,
)


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password_hash: str


class UserResponse(UserBase):
    model_config = ConfigDict(
        from_attributes=True,
    )
