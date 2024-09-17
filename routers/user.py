from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import User, Task
from sqlalchemy import insert, select, update, delete
from app.schemas import CreateUser, UpdateUser
from slugify import slugify

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.execute(select(User).where(User.username == user.username)).scalar()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    user_slug = slugify(user.username)
    db.execute(insert(User).values(
        username=user.username,
        firstname=user.firstname,
        lastname=user.lastname,
        age=user.age,
        slug=user_slug
    ))
    db.commit()
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.get("/all_users")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.execute(select(User)).scalars().all()
    return users


@router.get("/{user_id}")
async def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(select(User).where(User.id == user_id)).scalar()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/update/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.execute(select(User).where(User.id == user_id)).scalar()
    if existing_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updates = user.dict(exclude_unset=True)
    if 'username' in updates:
        updates['slug'] = slugify(updates['username'])

    db.execute(update(User).where(User.id == user_id).values(**updates))
    db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "User update is successful"}


@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.execute(select(User).where(User.id == user_id)).scalar()
    if existing_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Сначала удаляем все связанные Task
    db.execute(delete(Task).where(Task.user_id == user_id))
    db.commit()

    # Затем удаляем пользователя
    db.execute(delete(User).where(User.id == user_id))
    db.commit()

    return {"detail": "User and associated tasks deleted successfully"}
