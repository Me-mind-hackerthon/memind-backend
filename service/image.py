import os, boto3
from fastapi import HTTPException, status
from sqlmodel import select
from uuid import uuid4

from models import Image

class ImageHandler():
    def __init__(self, session):
        self.session = session
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id = os.environ["aws_access_key_id"],
            aws_secret_access_key = os.environ["aws_secret_access_key"]
        )

    def __upload_image_to_s3_bucket(self, image):
        file_name = uuid4().hex
        self.s3_client.upload_fileobj(
            image.file,
            os.environ["bucket_name"],
            file_name, 
            ExtraArgs={
                "ContentType": image.content_type
            }
        )

        image_url = f"https://{os.environ['bucket_name']}.s3.ap-northeast-2.amazonaws.com/{file_name}"
        return image_url

    def save_url_to_db(self, conversation_id, image):
        image_url = self.__upload_image_to_s3_bucket(image)

        image = Image(
            image_url = image_url,
            conversation_id = conversation_id
        )

        try:
            self.session.add(image)
            self.session.commit()
        except Exception:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND, detail = "no such conversation id"
            )

        return {
            "image_url": image_url
        }

    def get_image_list(self, conversation_id):
        image_object = select(Image).where(Image.conversation_id == conversation_id)
        image_object = self.session.exec(image_object).all()

        return {
            "photos": image_object
        }