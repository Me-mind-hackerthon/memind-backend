# daily report 관리와 midjourney image 관리 모델
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, List
from uuid import uuid4

from .talk import Conversation

class Report(SQLModel, table = True):
    conversation_id: str = Field(foreign_key = Conversation.conversation_id)
    report_id: str = Field(primary_key = True)
    summary: str
    mid_id: str = Field(default = None)
    keyword: List[str] = Field(sa_column = Column(JSON))

class Midjourney_image(SQLModel, table = True):
    mid_id: str = Field(primary_key = True)
    mid_image_url: Optional[str] = Field(default = None, nullable = True)

class Emotion(SQLModel, table = True):
    report_id: str = Field(foreign_key = Report.report_id)
    emotion_id: str = Field(default_factory = uuid4().hex, primary_key = True)
    happiness: int
    excitement: int
    anticipation: int
    boredom: int
    no_fun: int
    sadness: int
    suffering: int
    anger: int