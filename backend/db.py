from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Создание движка для базы данных SQLite
engine = create_engine('sqlite:///taskmanager.db', echo=True)

# Создание локальной сессии
SessionLocal = sessionmaker(bind=engine)


# Базовый класс для других моделей
class Base(DeclarativeBase):
    pass