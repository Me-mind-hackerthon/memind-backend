from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from auth import HashPassword
from database.connection import get_session
from service import userHandler
from schema import SignUpSchema, TokenResponse, messageOnlySchema

user_router = APIRouter(
    prefix = "/user", tags = ["user"]
)

@user_router.post("/signup")
def sign_user_up(user: SignUpSchema, session = Depends(get_session)) -> messageOnlySchema:
    result = userHandler(session).sign_up(user.user_id, user.password)

    return result

@user_router.post("/signin")
def sign_user_in(user: OAuth2PasswordRequestForm = Depends(), session = Depends(get_session)) -> TokenResponse:
    result = userHandler(session).sign_in(user)

    return result