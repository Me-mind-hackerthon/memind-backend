from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from models import User
from auth import hash_password, create_access_token

class userHandler:
    def __init__(self, session):
        self.session = session

    def sign_up(self, user_id, password):
        user_exist = select(User).where(User.user_id == user_id)
        user_exist = self.session.exec(user_exist).first()
        hashed_password = hash_password.HashPassword().create_hash(password)

        try:
            user = User(
                user_id = user_id,
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
        try:
            user_exist = select(User).where(User.user_id == user.username)
            user_exist = self.session.exec(user_exist).first()
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "user not found"
            )

        if(hash_password.HashPassword().verify_hash(user.password, user_exist.password)):
            access_token = create_access_token(user_exist.user_id)
            return {
                "access_token": access_token,
                "token_type": "Bearer"
            }
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "invalid details passed"
        )