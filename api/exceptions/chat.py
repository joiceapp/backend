from fastapi import status

from .api_exception import APIException


class ChatNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Chat not found"
    description = "This chat does not exist."

