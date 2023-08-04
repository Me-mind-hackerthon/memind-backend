from fastapi import Depends, APIRouter, UploadFile, File

from database.connection import get_session
from service import ImageHandler, ReportHandler
from schema import MidjourneyRequestsIn, messageOnlySchema, MidjourneyUpdateIn

image_router = APIRouter(
    prefix = "/api/image", tags = ["image"]
)

@image_router.post("/upload")
def upload_image(conversation_id: str, image: UploadFile = File(...), session = Depends(get_session)):
    result = ImageHandler(session).save_url_to_db(conversation_id, image)

    return result

@image_router.post("/create")
def create_midjourney_request_id(request: MidjourneyRequestsIn, session = Depends(get_session)) -> messageOnlySchema:
    result = ReportHandler(session, request.conversation_id).create_request_id(request.request_id)

    return result

@image_router.post("/update-image")
def update_midjourney_image(request: MidjourneyUpdateIn, session = Depends(get_session)) -> messageOnlySchema:
    result = ReportHandler(session, request.conversation_id).create_request_id(request.midjourney_url)

    return result