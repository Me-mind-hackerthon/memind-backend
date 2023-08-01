from sqlmodel import SQLModel

class SignUpSchema(SQLModel, table = False):
    user_id: str
    password: str

class TokenResponse(SQLModel, table = False):
    access_token: str
    token_type: str