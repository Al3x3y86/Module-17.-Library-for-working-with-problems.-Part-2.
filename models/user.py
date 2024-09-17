from app.backend.db import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    slug = Column(String, unique=True, index=True)

    tasks = relationship("Task", back_populates="user", cascade="all, delete, delete-orphan")

