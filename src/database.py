from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./user_devices.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

BaseDBModel = declarative_base()
