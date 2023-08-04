from sqlmodel import SQLModel

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