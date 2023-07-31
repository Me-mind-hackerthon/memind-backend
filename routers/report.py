from fastapi import APIRouter, Depends

from service import ReportHandler
from database.connection import get_session

report_router = APIRouter(
    prefix = "/report", tags = ["report"]
)

@report_router.get("/{report_id}")
def get_report(report_id: int, user_id, conversation_id, session = Depends(get_session)):
    result = ReportHandler(session, user_id, conversation_id).get_dailyreport(report_id)

    return result

@report_router.delete("/{report_id}")
def delete_report(session = Depends(get_session)):
    pass

@report_router.post("/create-daily")
def create_report(user_id, conversation_id, session = Depends(get_session)):
    result = ReportHandler(session, user_id, conversation_id).create_dailyreport()

    return result