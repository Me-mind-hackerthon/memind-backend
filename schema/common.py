from sqlmodel import SQLModel

class messageOnlySchema(SQLModel, table = False):
    message: str