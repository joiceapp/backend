from fastapi import status

from .api_exception import APIException


class ProviderNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Provider not found"
    description = "OAuth provider could not be found."



