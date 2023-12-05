import boto3, os
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from sqlmodel import select
from uuid import uuid4

from models import Image
from exception import NoSuchConversationIdError
from schema import ConversationInfoSchema
from service import ObjectCreator

class ObjectUploader(ABC):
    """ object를 다양한 저장소에 업로드하기 위한 인터페이스 """
    def __init__(self, session) -> None:
        self.session = session

    @abstractmethod
    def upload_object(self, obj):
        pass

class S3Uploader(ObjectUploader):
    def __init__(self, session) -> None:
        super().__init__(session)
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id = os.environ["aws_access_key_id"],
            aws_secret_access_key = os.environ["aws_secret_access_key"]
        )

    def upload_object(self, obj) -> str:
        """ image를 s3에 업로드하고 url을 리턴하는 함수"""
        file_name = uuid4().hex
    
        self.s3_client.upload_fileobj(
            obj.file,
            os.environ["bucket_name"],
            file_name, 
            ExtraArgs={
                "ContentType": obj.content_type
            }
        )

        image_url = f"https://{os.environ['bucket_name']}.s3.{os.environ['region']}.amazonaws.com/{file_name}"

        return image_url

class ImageCreator(ObjectCreator):
    def __init__(self, session) -> None:
        super().__init__(session)

    async def create_object(self, object_info):
        # db에 추가하기 위하여 Image 모델 객체 생성
        image_object = Image(
            image_url = object_info["image_url"],
            conversation_id = object_info["conversation_id"]
        )

        # db에 추가
        try:
            self.session.add(image_object)
            self.session.commit()

        # 존재하지 않는 conversation_id일 경우, 오류 발생
        except Exception:
            raise NoSuchConversationIdError

class ImageUploadController:
    def __init__(self, session, object_uploader) -> None:
        self.session = session
        self.object_uploader = object_uploader

    def upload_image_controll(self, obj, conversation_info) -> Dict[str, str]:
        image_url = self.object_uploader.upload_object(obj)

        object_info = {
            "image_url": image_url,
            "conversation_id": conversation_info.conversation_id
        }

        ImageCreator(self.session).create_object(object_info)

        return object_info

class ImageListLoader:
    def __init__(self, session) -> None:
        self.session = session

    async def get_image_list(self, conversation_info: ConversationInfoSchema) -> Dict[str, List[Any]]:
        """ input으로 받은 conversation_id에 해당하는 conversation에서 user가 업로드한 image들의 정보를 리턴하는 함수"""

        image_object = select(Image).where(Image.conversation_id == conversation_info.conversation_id)
        image_list = self.session.exec(image_object).all()

        return {
            "photos": image_list
        }