from fastapi import FastAPI
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine
import os, pymysql

from routers import talk_router, report_router, image_router, user_router

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app.include_router(router =  talk_router)
app.include_router(router = report_router)
app.include_router(router = user_router)
app.include_router(router = image_router)

@app.on_event("startup")
def on_startup():
    database_file = os.environ["DB_NAME"]
    database_connection_string = f"sqlite:///{database_file}"
    engine_url = create_engine(database_connection_string, echo = True)

    SQLModel.metadata.create_all(engine_url)