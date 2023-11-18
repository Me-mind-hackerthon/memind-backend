from fastapi import HTTPException, status

from .common import AlreadyExist, NotFoundError

class SignInFailedError(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Invalid Sign in details passed"

class UserAlreadyExist(AlreadyExist):
    def __init__(self):
        super().__init__()
        self.detail = "User with Id provided exist already"

class UserNotFound(NotFoundError):
    def __init__(self):
        super().__init__()
        self.detail = "User Not found"

class NicknameAlreadyExist(AlreadyExist):
    def __init__(self):
        super().__init__()
        self.detail = "Nickname already Exist"