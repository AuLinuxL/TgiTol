from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.models import Base
from util import get_conf_path

session = None
isInited = False

def _init_db():
    global session,isInited
    db_path = get_conf_path('TgiTol.db')
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    isInited = True

def get_session():
    if not session or not isInited:
        _init_db()
    return session

def close_session():
    global session, isInited
    if session:
        session.close()
        session = None
        isInited = False
