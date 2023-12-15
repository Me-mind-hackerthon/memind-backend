from fastapi import APIRouter, Depends

from service import DailyReportCreator, ReportDeletor, ReportLoader
from schema import ReportInSchema, GetReportOutSchema, MessageOnlySchema, KeywordSchema
from database.connection import get_session
from auth import authenticate

report_router = APIRouter(
    prefix = "/api/report", tags = ["report"]
)

@report_router.get("/{report_id}")
async def get_report(report_id, user: str = Depends(authenticate), session = Depends(get_session)) -> GetReportOutSchema:
    result = await ReportLoader(session).get_report(report_id)

    return result

@report_router.delete("/{report_id}")
async def delete_report(report_input: ReportInSchema, user: str = Depends(authenticate), session = Depends(get_session)) -> MessageOnlySchema:
    result = await ReportDeletor(session).delete_report(report_input.report_id)

    return result

@report_router.post("/create-daily")
async def create_report(report_input: ReportInSchema, user: str = Depends(authenticate), session = Depends(get_session)) -> KeywordSchema:
    result = await DailyReportCreator(session).create_dailyreport()

    return result