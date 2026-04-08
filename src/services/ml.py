from pathlib import Path

import asyncio

import onnxruntime as ort
import numpy as np

from exceptions.ml import ModelInferenceError
from schemas import PredictRequest

from core.logging import logger


BASE_DIR = Path(__file__).parent.parent
ML_PATH = str(BASE_DIR / "ml" / "diabetes_model.onnx")


class MLService:
    def __init__(self, ml_path: str) -> None:
        try:
            self.ml_session = ort.InferenceSession(
                path_or_bytes=ml_path,
                providers=["CPUExecutionProvider"],
            )
            self.input_name = self.ml_session.get_inputs()[0].name

        except Exception as e:
            logger.exception(f"Ошибка инициализации ML модели: {e}")
            raise RuntimeError("Ошибка инициализации ML модели")

    def _sync_predict(self, schema: PredictRequest) -> int:
        try:
            data = schema.model_dump()
            data_array = np.array(
                [
                    [
                        data["Pregnancies"],
                        data["Glucose"],
                        data["BMI"],
                        data["Age"],
                    ]
                ],
                dtype=np.float32,
            )

            output = self.ml_session.run(None, {self.input_name: data_array})
            prediction = int(output[0][0] > 0.5)

            return prediction

        except Exception as e:
            logger.exception(f"Ошибка ML инференса: {e}")
            raise ModelInferenceError()

    async def predict(self, schema: PredictRequest) -> int:
        loop = asyncio.get_running_loop()

        return await loop.run_in_executor(
            None,
            self._sync_predict,
            schema,
        )


ml_service = MLService(ml_path=ML_PATH)