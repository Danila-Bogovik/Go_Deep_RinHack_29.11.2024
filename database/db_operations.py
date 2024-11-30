from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

def get_engine(db_path: str = "sqlite:///bank_data.db"):
    """
    Создает движок базы данных.
    :param db_path: Путь к файлу базы данных SQLite.
    :return: SQLAlchemy engine.
    """
    return create_engine(db_path)


def create_database(engine):
    """
    Создает все таблицы в базе данных.
    :param engine: SQLAlchemy engine.
    """
    Base.metadata.create_all(engine)


def get_session(engine):
    """
    Возвращает сессию для работы с базой данных.
    :param engine: SQLAlchemy engine.
    :return: SQLAlchemy session.
    """
    Session = sessionmaker(bind=engine)
    return Session()
