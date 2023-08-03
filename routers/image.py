from fastapi import Depends, APIRouter, UploadFile, File

from database.connection import get_session
from service import ImageHandler

image_router = APIRouter(
    prefix = "/api/image", tags = ["image"]
)

@image_router.post("/upload")
def upload_image(conversation_id: str, image: UploadFile = File(...), session = Depends(get_session)):
    result = ImageHandler(session).save_url_to_db(conversation_id, image)

    return result