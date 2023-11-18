from sqlmodel import SQLModel

class UserInfo(SQLModel, table = False):
    nickname: str
    password: str

class TokenResponse(SQLModel, table = False):
    access_token: str
    token_type: str