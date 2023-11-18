from uuid import uuid4
import os
from sqlmodel import select
import openai
from datetime import datetime, date
from typing import Dict, List, Any

from models import Conversation, Message
from exception import ConversationNotFound, NoSuchConversationIdError

class DateParser:
    @staticmethod
    def parsing_date(date) -> datetime:
        """ date 정보를 year과 month로 파싱하는 함수 """
        return datetime.strptime(date, "%Y-%m-%d")

class EnoughJudge:
    @staticmethod
    def is_enough(conversation_lenght) -> bool:
        return conversation_lenght > 13

class MonthlyConversationLoader:
    def __init__(self, session) -> None:
        self.session = session

    def _get_conversation_list(self, date_object, nickname):
        conversation_object = select(Conversation).where(
            Conversation.nickname == nickname,
            Conversation.year == date_object.year,
            Conversation.month == date_object.month
        )

        return self.session.exec(conversation_object).all()

    async def get_conversation_by_month(self, date, nickname) -> Dict[str, List[Any]]:
        """ 해당 월에 나눈 대화 목록을 리턴하는 함수 """
        date_object = DateParser.parsing_date(date)
        conversation_list = self._get_conversation_list(date_object, nickname)

        if(not conversation_list):
            raise ConversationNotFound

        return {
            "conversation_list": conversation_list
        }

class FullMessageLoader:
    def __init__(self, session) -> None:
        self.session = session

    def get_all_full_messages(self, conversation_id) -> List[Any]:
        """ 해당 conversation에서 나누었던 message들을 모두 리턴하는 함수 """
        try:
            message_object = select(Message).where(Message.conversation_id == conversation_id)
            messages = self.session.exec(message_object).all()
        except Exception as e:
            raise NoSuchConversationIdError

        return messages

class MessageSender:
    def __init__(self):
        openai.api_key(os.environ["GPT_APIKEY"])
        self.premessage = [
                {"role": "system", "content": "너는 친절한 심리상담가야. 사용자에게 오늘 하루는 어땠는지 물어보고 사용자가 응답하면 더 자세히 물어봐주고 위로해주는 상담가의 역할을 해줘. 사용자에게 보내는 너의 첫 메세지는 '안녕하세요! 오늘 하루는 어땠나요?'로 고정이야. 사용자의 응답에 적절하게 반응해주고 항상 더 자세히 질문해줘야 해. 그리고 2번 이상 응답을 받으면, '충분히 이야기를 나눈 것 같네요. 오늘 하루를 평가한다면 몇 점을 주시겠어요?'라는 말로 대화를 마무리해줘"},
                {"role": "user", "content": "안녕"}
            ]

    async def send_message_to_chatgpt(self, messages = None):
        # OpenAI GPT-3.5 Turbo 모델에 대화를 요청합니다.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = self.premessage.extend(messages)
        )

        return response["choices"][0]["message"]["content"]
        
class ConversationStarter:
    def __init__(self, session):
        self.session = session

    def _get_conversation_id_by_date(self, date, nickname) -> str:
        """ 해당 일자에 conversation_id를 리턴하는 함수 """
        date_object = DateParser.parsing_date(date)

        conversation_object = select(Conversation).where(Conversation.nickname == nickname).where(Conversation.year == date_object.year).where(Conversation.month == date_object.month).where(Conversation.day == date_object.day)
        conversation_object = self.session.exec(conversation_object).first()

        return conversation_object.conversation_id

    # conversation 생성, message load, 길이 check
    async def start_conversation(self, date, nickname) -> Dict[str, Any]:
        """ conversation이 있으면, 대화 내용을 리턴하고, 없으면 새로 conversation을 생성하는 함수 """
        conversation_id = self._get_conversation_id_by_date(date, nickname)

        # conversation이 존재하지 않는 경우, 새로 conversation 생성
        if(not conversation_id):
            conversation_id = uuid4().hex
            conversation = Conversation(
                nickname = nickname,
                conversation_id = conversation_id
            )

            self.session.add(conversation)
            self.session.commit()

            response = MessageSender().send_message_to_chatgpt()

            MessageCreator().create_message(conversation_id, 0, False, response)

        chat_history = FullMessageLoader().get_all_full_messages(conversation_id)

        return {
            "conversation_id": conversation_id,
            "chat_history": chat_history,
            "is_enough": EnoughJudge.is_enough(len(chat_history))
        }

class MessageGetter:
    def __init__(self, session) -> None:
        self.session = session

    async def classify_writer(self, conversation_id):
        """ message들을 화자에 따라서 분류하여 리턴하는 함수 """
        chat_history = []
        messages = FullMessageLoader().get_all_full_messages(conversation_id)
    
        for m in messages:
            if(m.is_from_user):
                role = "user"
            elif(not m.is_from_user):
                role = "assistant"

            chat_history.append({"role": role, "content": m.message})

        return chat_history

class MessageCreator:
    def __init__(self, session):
        self.session = session

    async def create_message(self, conversation_id, order, is_from_user, message) -> None:
        """ 채팅 이력을 저장하는 함수 """
        message_object = Message(
            conversation_id = conversation_id,
            order = order,
            is_from_user = is_from_user,
            message = message
        )

        try:
            self.session.add(message_object)
            self.session.commit()
        except Exception as e:
            raise NoSuchConversationIdError

class MessageRespondent:
    def __init__(self, session):
        self.session = session

    async def answer_conversation(self, user_answer, conversation_id) -> Dict[str, Any]:
        """ 사용자의 응답에 대한 AI의 응답을 리턴하는 함수 """
        # 이전 대화 내역이 있으면 채팅에 추가합니다.
        messages = FullMessageLoader().get_all_full_messages(conversation_id)

        # 사용자 입력을 채팅에 추가합니다.
        messages.append({"role": "user", "content": user_answer})
        order = len(messages)
        await MessageCreator().create_message(conversation_id, order, user_answer, True)
    
        # OpenAI GPT-3.5 Turbo 모델에 대화를 요청합니다.
        response = await MessageSender().send_message_to_chatgpt(messages)

        await MessageCreator().create_message(conversation_id, order + 1, False, response)

        # 챗봇의 답변을 사용자 메시지와 함께 반환합니다.
        return {
            "message": response,
            "is_enough": EnoughJudge.is_enough(order)
        }