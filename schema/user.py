from sqlmodel import SQLModel

class SignUpSchema(SQLModel, table = False):
    user_id: str
    password: str