from sqlalchemy import Integer, String, Boolean, Column
from src.database import BaseDBModel

class tableUser(BaseDBModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, unique=True, index=True)
    password = Column(String, unique=False, index=False)
    is_admin = Column(Boolean, unique=False, index=False, default=False)
    is_deleted = Column(Boolean, unique=False, index=False, default=False)
    accessToken = Column(String, unique=False, index=False)

class DogsUser(BaseDBModel):
    __tablename__ = "dogsUsers"

    dogid = Column(Integer, primary_key=True)
    characteristic = Column(String, unique=False, index=False)
    coordinates = Column(String, unique=False, index=False)
    last_send = Column(String, unique=False, index=False)
    place = Column(String, unique=False, index=True)
    is_deleted = Column(Boolean, default=True)
    accessToken = Column(String, unique=False, index=False)

class Tasks(BaseDBModel):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    upload_user_id = Column(Integer)
    dog_id = Column(Integer)
    goal = Column(String, unique=False, index=False)
    done = Column(Boolean, default=True)

class Responses(BaseDBModel):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True)
    do_user_id = Column(Integer)
    task_id = Column(Integer)
    comment = Column(String, unique=False, index=False)
    photo = Column(String, unique=False, index=False)