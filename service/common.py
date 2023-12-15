import os
import json
import openai

from abc import ABC, abstractmethod

class ObjectCreator(ABC):
    def __init__(self, session) -> None:
        self.session = session

    @abstractmethod
    async def create_object(self, object_info):
        pass

class MessageSender:
    def __init__(self):
        openai.api_key(os.environ["GPT_APIKEY"])

    @staticmethod
    async def send_message(self, chat_data):
        # OpenAI GPT-3.5 Turbo 모델에 대화를 요청합니다.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_data
        )

        # 모델의 답변을 가져옵니다.
        assistant_response = response['choices'][0]['message']['content']
        assistant_response = json.loads(assistant_response)

        return assistant_response