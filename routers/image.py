# image 관리를 위한 api router
from fastapi import Depends, APIRouter, UploadFile, File

from database.connection import get_session
from service import S3Uploader, ImageUploadController, ImageListLoader
from schema import ConversationInfoSchema, ImageUploadOutInfo, ImageListOutSchema

image_router = APIRouter(
    prefix = "/api/image", tags = ["image"]
)

@image_router.post("/upload", response_model = ImageUploadOutInfo)
async def upload_image(conversation_info: ConversationInfoSchema, image: UploadFile = File(...), session = Depends(get_session)):
    s3_uploader = S3Uploader(session)
    result = await ImageUploadController(session, s3_uploader).upload_image_controll(image, conversation_info)

    return result

@image_router.post("/get-list", response_model = ImageListOutSchema)
async def get_image(conversation_info: ConversationInfoSchema, session = Depends(get_session)):
    result = await ImageListLoader(session).get_image_list(conversation_info)

    return result