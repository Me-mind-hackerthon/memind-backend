from sqlmodel import SQLModel
from typing import List

class ReportInSchema(SQLModel, table = False):
    conversation_id: str

class getReportOutSchema(SQLModel, table = False):
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
    midjourney_image: str
    keyword: List[str]

class KeywordSchema(SQLModel, table = False):
    message: str
    keyword: List[str]