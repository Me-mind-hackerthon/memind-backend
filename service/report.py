from sqlmodel import select
import os
import openai
import json

from service import ConversationHandler
from models import DailyReport, Message

class ReportHandler:
    def __init__(self, session, user_id, conversation_id):
        self.user_id = user_id
        self.session = session
        self.conversation_id = conversation_id
        openai.api_key = os.environ["GPT_APIKEY"]

    def __get_chat_history(self, conversation_id):
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

    def __set_gpt(self):
        messages = [
            {"role": "system", "content": "너는 친절한 심리상담가야. 사용자의 응답에 대해서 더 자세히 물어봐주고 위로해주는 상담가의 역할을 해줘. 단, 위로보다는 더 자세히 물어봐주는 경우가 더 많아야 해. 그리고 2줄 이상 말하지마"},
            {"role": "user", "content": "안녕"}
        ]

        # 이전 대화 내역이 있으면 채팅에 추가합니다.
        chat_history = self.__get_chat_history(self.conversation_id)
        messages.extend(chat_history)

        return messages

    def get_emotion_score(self):
        system_message = """
            당신은 훌륭한 감정 분류기 AI 서비스입니다. 당신은 대화 내용에서 감정을 감지하고 대화의 다양한 감정 측면에 JSON 형식으로 답변합니다.

            example: {
                "emotions":
                    "happiness":<0-100>,
                    "excitement":<0-100>,
                    "anticipation":<0-100>,
                    "boredom":<0-100>,
                    "no_fun":<0-100>,
                    "sadness":<0-100>,
                    "suffering":<0-100>,
                    "anger":<0-100>
            }
        """
        chat_data = self.__set_gpt()
        command = """
            지금까지의 대화를 평가해줘. 결과는 아래와 같은 형태의 JSON 포맷만 내보내줘. JSON 형식 외에 다른 말은 하지마.
            {
                "emotions":
                    "happiness":<0-100>,
                    "excitement":<0-100>,
                    "anticipation":<0-100>,
                    "boredom":<0-100>,
                    "no_fun":<0-100>,
                    "sadness":<0-100>,
                    "suffering":<0-100>,
                    "anger":<0-100>
            }
        """
        chat_data.extend([{"role": "system", "content": system_message}, {"role": "user", "content": command}])

        # OpenAI GPT-3.5 Turbo 모델에 대화를 요청합니다.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_data
        )

        # 모델의 답변을 가져옵니다.
        assistant_response = response['choices'][0]['message']['content']
        print(assistant_response)
        assistant_response = json.loads(assistant_response)

        return assistant_response

    def create_summary(self):
        system_message = "당신은 훌륭한 요약 생성기입니다. 지금까지의 대화 내용을 요약해서 간단한 일기로 작성해주세요. 일기는 1인칭 주인공 시점으로 작성됩니다."
        chat_data = self.__set_gpt()
        command = "지금까지의 대화 내용을 바탕으로 사용자의 하루를 간단한 일기를 작성해줘"
        chat_data.extend([{"role": "system", "content": system_message}, {"role": "user", "content": command}])

        # OpenAI GPT-3.5 Turbo 모델에 대화를 요청합니다.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_data
        )

        # 모델의 답변을 가져옵니다.
        assistant_response = response['choices'][0]['message']['content']
        print(assistant_response)

        return {
            "summary": assistant_response
        }

    def get_keyword(self):
        pass

    def create_dailyreport(self):
        emotion_list = self.get_emotion_score()["emotions"]
        summary = self.create_summary()

        dailyreport = DailyReport(
            conversation_id = self.conversation_id,
            happiness = emotion_list["happiness"],
            excitement = emotion_list["excitement"],
            anticipation = emotion_list["anticipation"],
            boredom = emotion_list["boredom"],
            no_fun = emotion_list["no_fun"],
            sadness = emotion_list["sadness"],
            suffering = emotion_list["suffering"],
            anger = emotion_list["anger"],
            summary = summary["summary"]
        )

        self.session.add(dailyreport)
        self.session.commit()

        report_object = select(DailyReport).where(DailyReport.conversation_id == self.conversation_id)
        report_id = self.session.exec(report_object).one().report_id

        return {
            "report_id": report_id
        }

    def get_dailyreport(self):
        report_object = select(DailyReport).where(DailyReport.conversation_id == self.conversation_id)
        report = self.session.exec(report_object).one()

        return report

    def delete_dailyreport(self):
        report_object = select(DailyReport).where(DailyReport.conversation_id == self.conversation_id)
        report_object = self.session.exec(report_object).one()

        self.session.delete(report_object)
        self.session.commit()

        return {
            "message": "리포트가 삭제되었습니다."
        }