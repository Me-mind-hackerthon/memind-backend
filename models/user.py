# user 정보 관리 모델
from sqlmodel import SQLModel, Field

class User(SQLModel, table = True):
    nickname: str = Field(primary_key = True)
    password: str