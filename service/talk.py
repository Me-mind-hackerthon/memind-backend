from uuid import uuid4
import os
from datetime import datetime, date
from typing import Dict, List, Any
from abc import ABC, abstractmethod

from sqlmodel import select
import openai

from models import Conversation, Message
from exception import ConversationNotFound, UserNotFound, NoSuchConversationIdError

class DateParser:
    @staticmethod
    def parsing_date(date) -> datetime:
        """ date 정보를 year과 month로 파싱하는 함수 """
        return datetime.strptime(date, "%Y-%m-%d")

class EnoughJudge:
    @staticmethod
    def is_enough(conversation_lenght) -> bool:
        return conversation_lenght > 13

# get_conversation_by_blah를 인터페이스로
class ConversationGetter(ABC):
    def __init__(self, session) -> None:
        self.session = session

    @abstractmethod
    def get_conversation(self, date, nickname):
        pass

class MonthlyConversationLoader(ConversationGetter):
    def __init__(self, session):
        super().__init__(session)

    async def get_conversation(self, date, nickname) -> List[Conversation]:
        date_object = DateParser.parsing_date(date)
    
        # 입력받은 월에 해당하는 conversation object를 쿼리
        conversation_list = self.session.exec(select(Conversation).where(
            Conversation.nickname == nickname,
            Conversation.year == date_object.year,
            Conversation.month == date_object.month
        )).all()

        if(not conversation_list):
            raise ConversationNotFound

        return conversation_list

class DailyConversationLoader(ConversationGetter):
    def __init__(self, session) -> None:
        super().__init__(session)

    async def get_conversation(self, date, nickname) -> List[Conversation]:
        """ 해당 일자에 conversation_id를 리턴하는 함수 """
        date_object = DateParser.parsing_date(date)

        conversation_list = self.session.exec(select(Conversation).where(
            Conversation.nickname == nickname,
            Conversation.year == date_object.year,
            Conversation.month == date_object.month,
            Conversation.day == date_object.day
        )).all()

        return conversation_list

class FullMessageLoader:
    def __init__(self, session) -> None:
        self.session = session

    async def get_all_full_messages(self, conversation_id) -> List[Message]:
        """ 해당 conversation에서 나누었던 message들을 모두 리턴하는 함수 """
        try:
            message_object = select(Message).where(Message.conversation_id == conversation_id)
            messages = self.session.exec(message_object).all()
        except Exception as e:
            raise NoSuchConversationIdError

        return messages

class MessageSender:
    def __init__(self) -> None:
        openai.api_key(os.environ["GPT_APIKEY"])
        self.premessage = [
                {"role": "system", "content": "너는 친절한 심리상담가야. 사용자에게 오늘 하루는 어땠는지 물어보고 사용자가 응답하면 더 자세히 물어봐주고 위로해주는 상담가의 역할을 해줘. 사용자에게 보내는 너의 첫 메세지는 '안녕하세요! 오늘 하루는 어땠나요?'로 고정이야. 사용자의 응답에 적절하게 반응해주고 항상 더 자세히 질문해줘야 해. 그리고 2번 이상 응답을 받으면, '충분히 이야기를 나눈 것 같네요. 오늘 하루를 평가한다면 몇 점을 주시겠어요?'라는 말로 대화를 마무리해줘"},
                {"role": "user", "content": "안녕"}
            ]

    async def send_message_to_chatgpt(self, messages = None) -> str:
        # OpenAI GPT-3.5 Turbo 모델에 대화를 요청합니다.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = self.premessage.extend(messages)
        )

        return response["choices"][0]["message"]["content"]
        
class ConversationStarter:
    def __init__(self, session) -> None:
        self.session = session

    # conversation 생성, message load, 길이 check
    async def start_conversation(self, date, nickname) -> Dict[str, Any]:
        """ conversation이 있으면, 대화 내용을 리턴하고, 없으면 새로 conversation을 생성하는 함수 """
        conversation_object = await DailyConversationLoader(self.session).get_conversation(date, nickname)

        # conversation이 존재하지 않는 경우, 새로 conversation 생성
        if(not conversation_object):
            object_info = {
                "nickname": nickname,
                "conversation_id": uuid4().hex
            }
            await ConversationCreator(self.session).create_object(object_info)

            response = await MessageSender().send_message_to_chatgpt()

            object_info["order"] = 0
            object_info["is_from_user"] = False
            object_info["message"] = response
            await MessageCreator(self.session).create_object(object_info)

        # 존재 하는 경우, 이전 대화 내용 로드
        chat_history = await FullMessageLoader().get_all_full_messages(object_info["conversation_id"])

        return {
            "conversation_id": object_info["conversation_id"],
            "chat_history": chat_history,
            "is_enough": EnoughJudge.is_enough(len(chat_history))
        }

class MessageGetter:
    def __init__(self, session) -> None:
        self.session = session

    async def classify_writer(self, conversation_id) -> List[Dict[str, str]]:
        """ message들을 화자에 따라서 분류하여 리턴하는 함수 """
        chat_history = []
        messages = FullMessageLoader(self.session).get_all_full_messages(conversation_id)
    
        for m in messages:
            chat_history.append({"role": "user" if m.is_from_user else "assistant", "content": m.message})

        return chat_history

class ObjectCreator(ABC):
    def __init__(self, session) -> None:
        self.session = session

    @abstractmethod
    async def create_object(self, object_info):
        pass

class MessageCreator(ObjectCreator):
    def __init__(self, session) -> None:
        super().__init__(session)

    async def create_object(self, object_info) -> None:
        message_object = Message(
            conversation_id = object_info["conversation_id"],
            order = object_info["order"],
            is_from_user = object_info["is_from_user"],
            message = object_info["message"]
        )

        try:
            self.session.add(message_object)
            self.session.commit()
        except Exception as e:
            raise NoSuchConversationIdError

class ConversationCreator(ObjectCreator):
    def __init__(self, session) -> None:
        super().__init__(session)

    async def create_object(self, object_info) -> None:
        conversation_object = Conversation(
            nickname = object_info["nickname"],
            conversation_id = object_info["conversation_id"]
        )

        try:
            self.session.add(conversation_object)
            self.session.commit()
        except Exception as e:
            raise UserNotFound

class MessageRespondent:
    def __init__(self, session) -> None:
        self.session = session

    async def answer_conversation(self, user_answer, conversation_id) -> Dict[str, Any]:
        """ 사용자의 응답에 대한 AI의 응답을 리턴하는 함수 """
        # 이전 대화 내역이 있으면 채팅에 추가합니다.
        messages = await FullMessageLoader().get_all_full_messages(conversation_id)

        # 사용자 입력을 채팅에 추가합니다.
        messages.append({"role": "user", "content": user_answer})
        order = len(messages)

        # message object를 생성하기 위한 args dict 생성
        object_info = {
            "conversation_id": conversation_id,
            "order": order,
            "is_from_user": True,
            "message": user_answer
        }
        await MessageCreator(self.session).create_object(object_info)
    
        # OpenAI GPT-3.5 Turbo 모델에 대화를 요청합니다.
        response = await MessageSender().send_message_to_chatgpt(messages)

        response_info = {
            "conversation_id": conversation_id,
            "order": order + 1,
            "is_from_user": False,
            "message": response
        }

        await MessageCreator(self.session).create_object(response_info)

        # 챗봇의 답변을 사용자 메시지와 함께 반환합니다.
        return {
            "message": response,
            "is_enough": EnoughJudge.is_enough(order)
        }