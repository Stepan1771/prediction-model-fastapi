from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)
from starlette import status

from core.config import settings

from api.depends import (
    get_current_user,
    get_ml_service,
)

from models import User

from schemas import (
    PredictRequest,
    PredictResponse,
)

from services import MLService


router = APIRouter(
    prefix=settings.api.v1.predict,
    tags=["Predict"],
)


@router.post(
    path="/",
    summary="Получение предсказания",
    response_model=PredictResponse,
    status_code=status.HTTP_201_CREATED,
)
async def predict(
        user: Annotated[
            User,
            Depends(get_current_user),
        ],
        service: Annotated[
            MLService,
            Depends(get_ml_service),
        ],
        schema: PredictRequest,
) -> PredictResponse:
    prediction = await service.predict(schema=schema)
    return PredictResponse(prediction=prediction)
