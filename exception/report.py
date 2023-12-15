from fastapi import HTTPException, status

from .common import NotFoundError

class NoSuchReportIdError(NotFoundError):
    def __init__(self):
        super().__init__()
        self.detail = "No Such Report Id"