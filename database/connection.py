from sqlmodel import SQLModel, Session, create_engine
import os

database_file = os.envrion["DATABASE_NAME"]
database_connection_string = f"sqlite:///{database_file}"
engine_url = create_engine(database_connection_string, echo = True)

SQLModel.metadata.create_all(engine_url)

def get_session():
    with Session(engine_url) as session:
        yield session