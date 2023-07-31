from sqlmodel import SQLModel

class ConversationInSchema(SQLModel, table = False):
    user_id: int
    user_answer: str
    conversation_id: str

class ConversationOutSchema(SQLModel, table = False):
    message: str