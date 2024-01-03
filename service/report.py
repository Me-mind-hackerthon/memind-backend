from sqlmodel import select
from abc import abstractmethod, ABC
import os
from uuid import uuid4
from fastapi import HTTPException, status

from service import MessageGetter, MessageSender, ObjectCreator
from models import Report, Emotion
from exception import NoSuchConversationIdError, NoSuchReportIdError

class InitialGPTSetting:
    def __init__(self, session):
        self.session = session
        self.premessages = [
            {"role": "system", "content": os.environ["chat_premessage"]},
            {"role": "user", "content": "안녕"}
        ]

    async def set_gpt(self, conversation_id):
        return self.premessages.extend(await MessageGetter(self.session).classify_writer(conversation_id))

class GPTReporter(ABC):
    def __init__(self, session, conversation_id):
        self.session = session
        self.conversation_id = conversation_id

    @abstractmethod
    async def get_report_factor(self):
        pass

class EmotionReporter(GPTReporter):
    def __init__(self, session, conversation_id):
        super().__init__(session, conversation_id)

    async def get_report_factor(self):
        chat_data = await InitialGPTSetting(self.session).set_gpt(self.conversation_id)

        return await MessageSender.send_message(chat_data.extend([{"role": "system", "content": os.environ["emotion_system_message"]}, {"role": "user", "content": os.environ["emotion_command_message"]}]))

class SummaryReporter(GPTReporter):
    def __init__(self, session, conversation_id):
        super().__init__(session, conversation_id)

    async def get_report_factor(self):
        chat_data = await InitialGPTSetting(self.session).set_gpt(self.conversation_id)

        return await MessageSender.send_message(chat_data.extend([{"role": "system", "content": os.environ["summary_system_message"]}, {"role": "user", "content": os.environ["summary_command_message"]}]))

class KeywordReporter(GPTReporter):
    def __init__(self, session, conversation_id):
        super().__init__(session, conversation_id)

    async def get_report_factor(self):
        chat_data = await InitialGPTSetting(self.session).set_gpt(self.conversation_id)

        return await MessageSender.send_message(chat_data.extend([{"role": "system", "content": os.environ["keyword_system_message"]}, {"role": "user", "content": os.environ["keyword_command_message"]}]))

class ReportCreator(ObjectCreator):
    def __init__(self, session) -> None:
        super().__init__(session)

    async def create_object(self, object_info):
        report_object = Report(
            conversation_id = object_info["conversation_id"],
            report_id = object_info["report_id"],
            summary = object_info["summary"],
            keyword = object_info["keyword"]
        )

        try:
            self.session.add(report_object)
            self.session.commit()
        except Exception as e:
            raise NoSuchConversationIdError

class EmotionCreator(ObjectCreator):
    def __init__(self, session) -> None:
        super().__init__(session)

    async def create_object(self, object_info):
        emotion_object = Emotion(
            report_id = object_info["report_id"],
            emotion_id = object_info["emotion_id"],
            happiness = object_info["happiness"],
            excitement = object_info["excitement"],
            anticipation = object_info["anticipation"],
            boredom = object_info["boredom"],
            no_fun = object_info["no_fun"],
            sadness = object_info["sadness"],
            suffering = object_info["suffering"],
            anger = object_info["anger"]
        )

        try:
            self.session.add(emotion_object)
            self.session.commit()
        except Exception as e:
            raise NoSuchReportIdError

class DailyReportCreator:
    def __init__(self, session) -> None:
        self.session = session

    async def create_dailyreport(self):
        try:
            emotion_list = await EmotionReporter(self.session).get_report_factor()["emotions"]
            keyword_list = await KeywordReporter(self.session).get_report_factor()["keyword"]
        except Exception:
            raise HTTPException(
                status_code = status.HTTP_417_EXPECTATION_FAILED, detail = "다시 시도해주세요"
            )

        summary = await SummaryReporter(self.session).get_report_factor()

        report_id = uuid4().hex
        object_info = {
            "conversation_id": self.conversation_id,
            "summary": summary,
            "keyword": keyword_list
        }

        await ReportCreator(self.session).create_object(object_info)
        await EmotionCreator(self.session).create_object(emotion_list.extend([{"report_id": report_id}]))

        return {
            "report_id": report_id,
            "keyword": keyword_list
        }

class ReportLoader:
    def __init__(self, session):
        self.session = session

    async def get_report(self, report_id):
        report_object = select(Report).where(Report.report_id == report_id)
        report = self.session.exec(report_object).first()

        if(not report):
            raise NoSuchReportIdError

        return report

class ReportDeletor:
    def __init__(self, session) -> None:
        self.session = session

    async def delete_report(self, report_id):
        report_object = select(Report).where(Report.report_id == report_id)
        report_object = self.session.exec(report_object).one()

        self.session.delete(report_object)
        self.session.commit()

        return {
            "message": "리포트가 삭제되었습니다."
        }

class MidjourneyIdCreator:
    def __init__(self, session):
        self.session = session

    async def create_midjourney_request_id(self, report_id, request_id):
        report_object = select(Report).where(Report.report_id == report_id)
        report_object = self.session.exec(report_object).first()

        if(not report_object):
            raise NoSuchReportIdError

        report_object.midjourney_image = request_id
        self.session.add(report_object)
        self.session.commit()
        self.session.refresh(report_object)

        return {
            "message": "success"
        }