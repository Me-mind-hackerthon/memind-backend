from fastapi import APIRouter, Depends

from database.connection import get_session
from service import ConversationHandler
from schema import ConversationInSchema, ConversationOutSchema

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
def answer_question(conversation_input: ConversationInSchema, session = Depends(get_session)) -> ConversationOutSchema:
    result = ConversationHandler(session = session, user_id = conversation_input.user_id).answer_conversation(conversation_input.user_answer, conversation_input.conversation_id)

    return result