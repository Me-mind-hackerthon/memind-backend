import boto3, os
from typing import Dict, List, Any
from sqlmodel import select
from uuid import uuid4

from models import Image
from exceptions import NoSuchConversationIdError
from schema import ConversationInfoSchema

class ImageSaver:
    def __init__(self, session) -> None:
        self.session = session
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id = os.environ["aws_access_key_id"],
            aws_secret_access_key = os.environ["aws_secret_access_key"]
        )

    def __upload_image_to_s3_bucket(self, image) -> str:
        """ image를 s3에 업로드하고 url을 리턴하는 함수"""

        file_name = uuid4().hex
    
        self.s3_client.upload_fileobj(
            image.file,
            os.environ["bucket_name"],
            file_name, 
            ExtraArgs={
                "ContentType": image.content_type
            }
        )

        image_url = f"https://{os.environ['bucket_name']}.s3.{os.environ['region']}.amazonaws.com/{file_name}"
        return image_url

    async def save_url_to_db(self, conversation_info: ConversationInfoSchema, image) -> Dict[str, str]:
        """ image의 s3 url을 해당 image가 속해있는 conversation_id와 함께 db에 저장하는 함수"""

        # image를 s3에 업로드하고 url을 생성
        image_url = self.__upload_image_to_s3_bucket(image)

        # db에 추가하기 위하여 Image 모델 객체 생성
        image = Image(
            image_url = image_url,
            conversation_id = conversation_info.conversation_id
        )

        # db에 추가
        try:
            self.session.add(image)
            self.session.commit()

        # 존재하지 않는 conversation_id일 경우, 오류 발생
        except Exception:
            raise NoSuchConversationIdError

        # db 추가 성공 시, image_url 리턴
        return {
            "image_url": image_url
        }

class ImageListHandler:
    def __init__(self, session) -> None:
        self.session = session

    async def get_image_list(self, conversation_info: ConversationInfoSchema) -> Dict[str, List[Any]]:
        """ input으로 받은 conversation_id에 해당하는 conversation에서 user가 업로드한 image들의 정보를 리턴하는 함수"""

        image_object = select(Image).where(Image.conversation_id == conversation_info.conversation_id)
        image_list = self.session.exec(image_object).all()

        return {
            "photos": image_list
        }