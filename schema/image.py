from sqlmodel import SQLModel

class ConversationInfoSchema(SQLModel, table = False):
    conversation_id: str

class ImageUploadOutInfo(SQLModel, table = False):
    image_url: str

class ImageListOutSchema(SQLModel, table = False):
    photos: list[str]

class MidjourneyRequestsIn(SQLModel, table = False):
    conversation_id: str
    request_id: str

class MidjourneyUpdateIn(SQLModel, table = False):
    conversation_id: str
    midjourney_url: str