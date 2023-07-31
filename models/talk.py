from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Conversation(SQLModel, table = True):
    user_id: str # 로그인 구현하고 user 테이블의 user_id와 연결
    conversation_id: str = Field(default = None, primary_key = True)
    Conversation_date: Optional[datetime] = Field(default_factory = datetime.today, nullable = False)

class Message(SQLModel, table = True):
    conversation_id: str = Field(foreign_key = Conversation.conversation_id)
    message_id: Optional[int] = Field(default = None, primary_key = True)
    order: int
    is_from_user: bool
    message: str