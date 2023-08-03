from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from models import User
from auth import hash_password, create_access_token

class userHandler:
    def __init__(self, session):
        self.session = session

    def get_user_info(self, nickname):
        try:
            user_exist = select(User).where(User.nickname == nickname)
            user_exist = self.session.exec(user_exist).one()
        except Exception as e:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "user not found"
            )

        return user_exist

    def sign_up(self, nickname, password):
        user_exist = select(User).where(User.nickname == nickname)
        user_exist = self.session.exec(user_exist).first()
        hashed_password = hash_password.HashPassword().create_hash(password)

        try:
            user = User(
                nickname = nickname,
                password = hashed_password
            )

            self.session.add(user)
            self.session.commit()

        except Exception:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = "user with id provided exists already"
            )

        return {
            "message": "user created successfully"
        }

    def sign_in(self, user):
        user_object = self.get_user_info(user.username)

        if(hash_password.HashPassword().verify_hash(user.password, user_object.password)):
            access_token = create_access_token(user_object.nickname)
            return {
                "access_token": access_token,
                "token_type": "Bearer"
            }
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "invalid details passed"
        )