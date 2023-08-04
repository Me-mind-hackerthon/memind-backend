from sqlmodel import SQLModel

class MidjourneyRequestsIn(SQLModel, table = False):
    conversation_id: str
    request_id: str

class MidjourneyUpdateIn(SQLModel, table = False):
    conversation_id: str
    midjourney_url: str