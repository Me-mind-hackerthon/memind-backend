from fastapi import APIRouter, Depends

from service import ReportHandler
from schema import ReportInSchema, getReportOutSchema, messageOnlySchema
from database.connection import get_session

report_router = APIRouter(
    prefix = "/report", tags = ["report"]
)

@report_router.get("/{conversation_id}")
def get_report(user_id, conversation_id, session = Depends(get_session)) -> getReportOutSchema:
    result = ReportHandler(session, user_id, conversation_id).get_dailyreport()

    return result

@report_router.delete("/{converssation_id}")
def delete_report(report_input: ReportInSchema, session = Depends(get_session)) -> messageOnlySchema:
    result = ReportHandler(session, report_input.user_id, report_input.conversation_id).delete_dailyreport()

    return result

@report_router.post("/create-daily")
def create_report(report_input: ReportInSchema, session = Depends(get_session)) -> messageOnlySchema:
    result = ReportHandler(session, report_input.user_id, report_input.conversation_id).create_dailyreport()

    return result