from fastapi import APIRouter, Depends

from database.connection import get_session
from service import ConversationHandler

talk_router = APIRouter(
    prefix = "/talk", tags = ["talk"]
)

@talk_router.post("/start")
def start_conversation(user_id, session = Depends(get_session)):
    result = ConversationHandler(session = session, user_id = user_id).start_conversation()

    return result

@talk_router.post("/end")
def end_conversation(session = Depends(get_session)):
    pass

@talk_router.post("/answer")
def answer_question(user_id, user_answer, conversation_id, session = Depends(get_session)):
    result = ConversationHandler(session = session, user_id = user_id).answer_conversation(user_answer, conversation_id)

    return result