from sqlmodel import SQLModel, Field
from typing import Optional
from models import Conversation

class DailyReport(SQLModel, table = True):
    conversation_id: Optional[str] = Field(foreign_key = Conversation.conversation_id)
    report_id: Optional[int] = Field(default = None, primary_key = True)
    happiness: int
    excitement: int
    anticipation: int
    boredom: int
    no_fun: int
    sadness: int
    suffering: int
    anger: int
    summary: str
    midjourney_image: Optional[str] = Field(default = None)