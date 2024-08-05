from fastapi import HTTPException, status


class PhoneNumberAlreadyExists(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = "Phone number already exists"