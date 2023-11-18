from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from auth import HashPassword, authenticate
from database.connection import get_session
from service import SignIn, SignUp, GetUserInfo, DuplicateHandler
from schema import TokenResponse, MessageOnlySchema, UserInfo

user_router = APIRouter(
    prefix = "/api/user", tags = ["user"]
)

@user_router.post("/signup")
async def sign_user_up(user: UserInfo, session = Depends(get_session)) -> MessageOnlySchema:
    result = await SignUp(session).sign_up(user)

    return result

@user_router.post("/signin")
async def sign_user_in(user: OAuth2PasswordRequestForm = Depends(), session = Depends(get_session)) -> TokenResponse:
    result = await SignIn(session).sign_in(user)

    return result

@user_router.get("/me")
async def get_user_info(user: str = Depends(authenticate), session = Depends(get_session)):
    result = await GetUserInfo(session).get_user_info(user)

    return result

@user_router.post("/nickname")
async def check_nickname(user: UserInfo, session = Depends(get_session)):
    result = await DuplicateHandler(session).check_nickname(user.nickname)

    return result