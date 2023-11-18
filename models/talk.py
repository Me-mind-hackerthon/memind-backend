# 대화 관리 모델
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date
from uuid import uuid4

from .user import User

class Conversation(SQLModel, table = True):
    nickname: str = Field(foreign_key = User.nickname)
    conversation_id: str = Field(default = None, primary_key = True)
    year: Optional[int] = Field(default_faactory = date.today().year, nullable = False)
    month: Optional[int] = Field(default_factory = date.today().month, nullable = False)
    day: Optional[int] = Field(default_factory = date.today().day, nullable = False)

class Message(SQLModel, table = True):
    conversation_id: str = Field(foreign_key = Conversation.conversation_id)
    message_id: Optional[str] = Field(default_factory = uuid4().hex, primary_key = True)
    message_timestamp: Optional[str] = Field(default_factory = datetime.now())
    order: int
    is_from_user: bool
    message: Optional[str]