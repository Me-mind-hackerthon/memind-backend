from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from auth import HashPassword, authenticate
from database.connection import get_session
from service import userHandler
from schema import SignUpSchema, TokenResponse, messageOnlySchema, UserInfo

user_router = APIRouter(
    prefix = "/api/user", tags = ["user"]
)

@user_router.post("/signup")
def sign_user_up(user: SignUpSchema, session = Depends(get_session)) -> messageOnlySchema:
    result = userHandler(session).sign_up(user.nickname, user.password)

    return result

@user_router.post("/signin")
def sign_user_in(user: OAuth2PasswordRequestForm = Depends(), session = Depends(get_session)) -> TokenResponse:
    result = userHandler(session).sign_in(user)

    return result

@user_router.get("/me")
def get_user_info(user: str = Depends(authenticate), session = Depends(get_session)):
    result = userHandler(session).get_user_info(user)

    return result

@user_router.post("/nickname")
def check_nickname(nickname: UserInfo, session = Depends(get_session)):
    result = userHandler(session).check_nickname(nickname.nickname)

    return result