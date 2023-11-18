from sqlmodel import SQLModel

class MessageOnlySchema(SQLModel, table = False):
    message: str