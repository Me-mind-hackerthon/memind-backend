from fastapi import APIRouter, Depends

from database.connection import get_session
from service import ConversationStarter, MonthlyConversationLoader, MessageRespondent
from schema import ConversationInSchema, ConversationOutSchema
from auth import authenticate

talk_router = APIRouter(
    prefix = "/api/talk", tags = ["talk"]
)

@talk_router.post("/start")
async def start_conversation(date: str, user: str = Depends(authenticate), session = Depends(get_session)):
    result = await ConversationStarter(session = session).start_conversation(date, user)

    return result

@talk_router.post("/answer")
async def answer_question(conversation_input: ConversationInSchema, user: str = Depends(authenticate), session = Depends(get_session)) -> ConversationOutSchema:
    result = await MessageRespondent(session = session).answer_conversation(conversation_input.user_answer, conversation_input.conversation_id)

    return result

@talk_router.post("/get-list")
async def get_conversation_list(conversation_date: str, user:str = Depends(authenticate), session = Depends(get_session)):
    result = MonthlyConversationLoader(session = session).get_conversation_by_month(conversation_date, user)

    return result