from fastapi import APIRouter, Depends
from sqlmodel import select

from auth.hash_password import HashPassword
from database.connection import get_session
from service import userHandler
from schema import SignUpSchema

user_router = APIRouter(
    prefix = "/user", tags = ["user"]
)

@user_router.post("/signup")
def sign_user_up(user: SignUpSchema, session = Depends(get_session)):
    result = userHandler(session).sign_up(user.user_id, user.password)

    return result