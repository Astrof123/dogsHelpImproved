from src.database import DBSession

def get_db_session():
    session = DBSession()
    try:
        yield session
    finally:
        session.close()