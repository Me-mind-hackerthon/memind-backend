from sqlmodel import SQLModel, Field

class User(SQLModel, table = True):
    user_id: str = Field(primary_key = True)
    password: str