from fastapi import status

from .api_exception import APIException


class EventNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Event not found"
    description = "Event with this ID could not be found."


class AlreadyParticipantException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Already Participant"
    description = "User already participate in this Event."
