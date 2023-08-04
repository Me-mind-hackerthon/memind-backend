from fastapi import APIRouter, Depends

from database.connection import get_session
from service import ConversationHandler
from schema import ConversationInSchema, ConversationOutSchema, GetConversationByMonth
from auth import authenticate

talk_router = APIRouter(
    prefix = "/api/talk", tags = ["talk"]
)

@talk_router.post("/start")
def start_conversation(date: str, user: str = Depends(authenticate), session = Depends(get_session)):
    result = ConversationHandler(session = session, nickname = user).start_conversation(date)

    return result

@talk_router.post("/end")
def end_conversation(user: str = Depends(authenticate), session = Depends(get_session)):
    pass

@talk_router.post("/answer")
def answer_question(conversation_input: ConversationInSchema, user: str = Depends(authenticate), session = Depends(get_session)) -> ConversationOutSchema:
    result = ConversationHandler(session = session, nickname = user).answer_conversation(conversation_input.user_answer, conversation_input.conversation_id)

    return result

@talk_router.post("/get-list")
def get_conversation_list(conversation_date: GetConversationByMonth, user:str = Depends(authenticate), session = Depends(get_session)):
    result = ConversationHandler(session = session, nickname = user).get_conversation_by_month(conversation_date.conversation_date)

    return result