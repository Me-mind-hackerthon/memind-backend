from fastapi import HTTPException, status

class NotFoundError(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_404_NOT_FOUND

class AlreadyExist(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_409_CONFLICT