from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import Task, User
from app.schemas import CreateTask, UpdateTask
from sqlalchemy import select, insert, update, delete
from slugify import slugify

router = APIRouter(prefix="/task", tags=["task"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_task(task: CreateTask, user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(select(User).where(User.id == user_id)).scalar()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    task_slug = slugify(task.title)
    db.execute(insert(Task).values(
        title=task.title,
        content=task.content,
        priority=task.priority,
        completed=task.completed,
        user_id=user_id,
        slug=task_slug
    ))
    db.commit()
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.get("/")
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.execute(select(Task)).scalars().all()
    return tasks


@router.get("/{task_id}")
async def task_by_id(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.execute(select(Task).where(Task.id == task_id)).scalar()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/update/{task_id}", status_code=status.HTTP_200_OK)
async def update_task(task_id: int, task: UpdateTask, db: Annotated[Session, Depends(get_db)]):
    existing_task = db.execute(select(Task).where(Task.id == task_id)).scalar()
    if existing_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    updates = task.dict(exclude_unset=True)
    if 'title' in updates:
        updates['slug'] = slugify(updates['title'])

    db.execute(update(Task).where(Task.id == task_id).values(**updates))
    db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "Task update is successful"}


@router.delete("/delete/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    existing_task = db.execute(select(Task).where(Task.id == task_id)).scalar()
    if existing_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.execute(delete(Task).where(Task.id == task_id))
    db.commit()
    return {"detail": "Task deleted successfully"}


@router.get("/user/{user_id}/tasks")
async def tasks_by_user_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(select(User).where(User.id == user_id)).scalar()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    tasks = db.execute(select(Task).where(Task.user_id == user_id)).scalars().all()
    return tasks
