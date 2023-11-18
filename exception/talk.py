from fastapi import HTTPException, status

from .common import NotFoundError

class ConversationNotFound(NotFoundError):
    def __init__(self):
        super().__init__()
        self.detail = "해당 월에 작성된 일기가 없습니다"