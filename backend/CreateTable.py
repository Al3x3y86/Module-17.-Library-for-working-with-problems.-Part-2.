from sqlalchemy.schema import CreateTable
from app.models.task import Task
from app.models.user import User
from app.backend.db import engine


print(CreateTable(Task.__table__).compile(engine))
print(CreateTable(User.__table__).compile(engine))
