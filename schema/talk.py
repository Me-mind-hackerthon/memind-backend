from sqlmodel import SQLModel

class CreateMessageInSchema(SQLModel, table = False):
    conversation_id: str
    order: int
    is_from_user: bool
    message: str

class ConversationInSchema(SQLModel, table = False):
    user_answer: str
    conversation_id: str

class ConversationOutSchema(SQLModel, table = False):
    message: str
    is_enough: bool