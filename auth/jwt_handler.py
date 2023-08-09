import time, os
from datetime import datetime

from fastapi import HTTPException, status
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv("../.env")

def create_access_token(user: str):
    payload = {
        "user": user,
        "expires": time.time() + 36000
    }

    token = jwt.encode(payload, os.environ["SECRET_KEY"], algorithm = "HS256")
    return token

def verify_access_token(token: str):
    try:
        data = jwt.decode(token, os.environ["SECRET_KEY"], algorithms = ["HS256"])
        expire = data.get("expires")

        if(expire is None):
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "no such token supplied"
            )

        if(datetime.utcnow() > datetime.utcfromtimestamp(expire)):
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "token expired"
            )

        return data

    except JWTError:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "invaild token"
        )