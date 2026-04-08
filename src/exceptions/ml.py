from .base import AppException


class ModelInferenceError(AppException):
    status_code = 500
    code = "MODEL_INFERENCE_ERROR"
    detail = "Ошибка при выполнении ML инференса"
