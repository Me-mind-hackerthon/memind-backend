from sqlmodel import SQLModel, Field

from .talk import Conversation

class Image(SQLModel, table = True):
    conversation_id: str = Field(foreign_key = Conversation.conversation_id)
    image_url: str = Field(primary_key = True)