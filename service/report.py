from sqlmodel import select
import os
import openai
import json
from fastapi import HTTPException, status

from service import ConversationHandler
from models import DailyReport, Message

class ReportHandler:
    def __init__(self, session, conversation_id):
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
            당신은 훌륭한 감정 평가기입니다. 당신은 대화 내용에서 대화의 다양한 감정 측면에 대해 점수를 매겨서 JSON 형식으로 답변합니다. 아래 example JSON 형식 이외에 다른 말은 하지 마세요. 그리고 더 많은 정보를 요구하지 마세요. 감정 평가가 불가능하다는 말도 안돼.

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
            지금까지의 대화를 아래 JSON 형식으로 평가해줘. 결과는 아래와 같은 형태의 JSON 포맷만 내보내줘. JSON 형식 외에 다른 말은 하지마.
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
        return {
            "summary": assistant_response
        }

    def get_keyword(self):
        system_message = """
            당신은 훌륭한 키워드 추출기입니다. 지금까지의 대화 내용 중에서 핵심 키워드를 명사와 형용사 형태로 추출해주세요. 결과는 아래와 같은 형태의 JSON 포맷 형식이고, 사용자에게 더 많은 정보를 요구하지 말고 아래 형태 외에 다른 말은 하지마.
            {
                "keyword": [첫번째 키워드, 두번째 키워드]
            }
        """
        chat_data = self.__set_gpt()
        command = """
            지금까지의 대화 내용을 바탕으로 핵심 키워드를 추출해줘. 결과는 아래와 같은 형태의 JSON 포맷만 내보내줘. JSON 형식 외에 다른 말은 하지마. '첫번째 키워드, 두번째 키워드'. 대화가 너무 짧아서 정보를 추출할 수 없더라고 적어도 단어 하나는 추출해 내야 해
            {
                "keyword": [첫번째 키워드, 두번째 키워드]
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
        assistant_response = json.loads(assistant_response)

        return assistant_response

    def create_dailyreport(self):
        try:
            emotion_list = self.get_emotion_score()["emotions"]
            keyword_list = self.get_keyword()
        except Exception:
            raise HTTPException(
                status_code = status.HTTP_417_EXPECTATION_FAILED, detail = "다시 시도해주세요"
            )
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
            summary = summary["summary"],
            keyword = keyword_list["keyword"]
        )

        self.session.add(dailyreport)
        self.session.commit()

        report_object = select(DailyReport).where(DailyReport.conversation_id == self.conversation_id)

        return {
            "message": "리포트가 생성되었습니다.",
            "keyword": keyword_list["keyword"]
        }

    def get_dailyreport(self):
        try:
            report_object = select(DailyReport).where(DailyReport.conversation_id == self.conversation_id)
            report = self.session.exec(report_object).one()
        except Exception:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "no such conversation id"
            )

        return report

    def delete_dailyreport(self):
        report_object = select(DailyReport).where(DailyReport.conversation_id == self.conversation_id)
        report_object = self.session.exec(report_object).one()

        self.session.delete(report_object)
        self.session.commit()

        return {
            "message": "리포트가 삭제되었습니다."
        }

    def create_request_id(self, request_id):
        try:
            report_object = select(DailyReport).where(DailyReport.conversation_id == self.conversation_id)
            report_object = self.session.exec(report_object).one()
        except Exception:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND, detail = "no such conversation id"
            )

        report_object.midjourney_image = request_id
        self.session.add(report_object)
        self.session.commit()
        self.session.refresh(report_object)

        return {
            "message": "success"
        }