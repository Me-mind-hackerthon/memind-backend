from uuid import uuid4
import os
from sqlmodel import select
from fastapi import HTTPException, status
import openai
from datetime import datetime, date

from models import Conversation, Message

class ConversationHandler:
    def __init__(self, session, nickname):
        self.session = session
        self.nickname = nickname
        # OpenAI GPT-3.5 Turbo API 인증 설정
        openai.api_key = os.environ["GPT_APIKEY"]

    def __parsing_date(self, date):
        date_object = datetime.strptime(date, "%Y-%m")

        return date_object.year, date_object.month

    def get_all_messages(self, conversation_id):
        chat_history = []
        message_object = select(Message).where(Message.conversation_id == conversation_id)
        messages = self.session.exec(message_object).all()

        for m in messages:
            if(m.is_from_user):
                role = "user"
            elif(not m.is_from_user):
                role = "assistant"

            chat_history.append({"role": role, "content": m.message})

        return chat_history

    def __get_all_full_messages(self, conversation_id):
        message_object = select(Message).where(Message.conversation_id == conversation_id)
        messages = self.session.exec(message_object).all()

        return messages

    def get_conversation_by_month(self, date):
        year, month = self.__parsing_date(date)
        conversation_object = select(Conversation).where(Conversation.nickname == self.nickname).where(Conversation.year == year).where(Conversation.month == month)
        conversation_list = self.session.exec(conversation_object).all()

        if(not conversation_list):
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND, detail = "해당 월에 작성된 일기가 없습니다"
            )

        return {
            "conversation_list": conversation_list
        }

    def create_message(self, conversation_id, order, message, is_from_user):
        message_object = Message(
            conversation_id = conversation_id,
            order = order,
            is_from_user = is_from_user,
            message = message
        )

        self.session.add(message_object)
        self.session.commit()

        return

    def __get_conversation_id_by_date(self, date):
        date_object = datetime.strptime(date, "%Y-%m-%d")

        try:
            conversation_object = select(Conversation).where(Conversation.year == date_object.year).where(Conversation.month == date_object.month).where(Conversation.day == date_object.day)
            conversation_object = self.session.exec(conversation_object).one()
            print(conversation_object)
        except Exception:
            return 0

        return conversation_object.conversation_id

    def start_conversation(self, date):
        is_created = self.__get_conversation_id_by_date(date)
        if(is_created):
            chat_history = self.__get_all_full_messages(is_created)

            if(len(chat_history) > 13):
                is_enough = True
            else:
                is_enough = False

            return {
                "conversation_id": is_created,
                "chat_history": chat_history,
                "is_enough": is_enough
            }

        conversation_id = uuid4().hex
        conversation = Conversation(
            nickname = self.nickname,
            conversation_id = conversation_id
        )

        self.session.add(conversation)
        self.session.commit()

        messages = [
            {"role": "system", "content": "너는 친절한 심리상담가야. 사용자에게 오늘 하루는 어땠는지 물어보고 사용자가 응답하면 더 자세히 물어봐주고 위로해주는 상담가의 역할을 해줘. 사용자에게 보내는 너의 첫 메세지는 '안녕하세요! 오늘 하루는 어땠나요?'로 고정이야. 사용자의 응답에 적절하게 반응해주고 항상 더 자세히 질문해줘야 해. 그리고 2번 이상 응답을 받으면, '충분히 이야기를 나눈 것 같네요. 오늘 하루를 평가한다면 몇 점을 주시겠어요?'라는 말로 대화를 마무리해줘"},
            {"role": "user", "content": "안녕"}
        ]

        # OpenAI GPT-3.5 Turbo 모델에 대화를 요청합니다.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        self.create_message(conversation_id, 0, response['choices'][0]['message']['content'], False)

        return {"conversation_id": conversation_id, "message": response['choices'][0]['message']['content']}

    def answer_conversation(self, user_answer, conversation_id):
        messages = [
            {"role": "system", "content": "너는 친절한 심리상담가야. 사용자의 응답에 대해서 더 자세히 물어봐주고 위로해주는 상담가의 역할을 해줘. 단, 위로보다는 더 자세히 물어봐주는 경우가 더 많아야 해. 그리고 2줄 이상 말하지마"},
            {"role": "user", "content": "안녕"}
        ]

        # 이전 대화 내역이 있으면 채팅에 추가합니다.
        chat_history = self.get_all_messages(conversation_id = conversation_id)
        messages.extend(chat_history)

        # 사용자 입력을 채팅에 추가합니다.
        user_message = {"role": "user", "content": user_answer}
        messages.append(user_message)

        # message object 추가
        order = len(messages)
        self.create_message(conversation_id, order, user_answer, True)
    
        # OpenAI GPT-3.5 Turbo 모델에 대화를 요청합니다.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        # 모델의 답변을 가져옵니다.
        assistant_response = response['choices'][0]['message']['content']

        self.create_message(conversation_id, order + 1, assistant_response, False)

        if(order > 13):
            is_enough = True
        else:
            is_enough = False

        # 챗봇의 답변을 사용자 메시지와 함께 반환합니다.
        return {
            "message": assistant_response,
            "is_enough": is_enough
        }