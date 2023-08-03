from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

from .user import User

class Conversation(SQLModel, table = True):
    nickname: str = Field(foreign_key = User.nickname)
    conversation_id: str = Field(default = None, primary_key = True)
    Conversation_date: Optional[datetime] = Field(default_factory = datetime.today, nullable = False)

class Message(SQLModel, table = True):
    conversation_id: str = Field(foreign_key = Conversation.conversation_id)
    message_id: Optional[int] = Field(default = None, primary_key = True)
    order: int
    is_from_user: bool
    message: str