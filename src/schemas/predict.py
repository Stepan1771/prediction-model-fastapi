from pydantic import (
    BaseModel,
    ConfigDict,
)


class PredictRequest(BaseModel):
    Pregnancies: int
    Glucose: float
    BMI: float
    Age: int


class PredictResponse(BaseModel):
    prediction: int

    model_config = ConfigDict(
        from_attributes=True
    )