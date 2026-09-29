from sqlalchemy.orm import sessionmaker
from models import db


SessionLocal = sessionmaker(bind=db)


def pegar_sessao():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()