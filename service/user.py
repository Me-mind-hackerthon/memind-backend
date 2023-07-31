from fastapi import HTTPException, status
from sqlmodel import select

from models import User
from auth import hash_password

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