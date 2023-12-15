from sqlmodel import SQLModel
from typing import List, Optional

class ReportInSchema(SQLModel, table = False):
    conversation_id: str

class GetReportOutSchema(SQLModel, table = False):
    conversation_id: str
    report_id: int
    happiness: int
    excitement: int
    anticipation: int
    boredom: int
    no_fun: int
    sadness: int
    suffering: int
    anger: int
    summary: str
    midjourney_image: Optional[str]
    keyword: List[str]

class KeywordSchema(SQLModel, table = False):
    message: str
    keyword: List[str]