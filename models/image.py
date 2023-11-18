from sqlmodel import SQLModel, Field

from .talk import Conversation, Message

class Image(SQLModel, table = True):
    image_id: str = Field(primary_key = True)
    conversation_id: str = Field(foreign_key = Conversation.conversation_id)
    message_id: str = Field(foreign_key = Message.message_id)
    image_url: str