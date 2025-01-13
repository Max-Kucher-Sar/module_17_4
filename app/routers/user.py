from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models.user import User
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(prefix='/user', tags=['user'])


@router.get('/', response_model=list[User])
async def all_users(db: Annotated[Session, Depends(get_db)]):
    query = select(User)
    result = db.execute(query)
    users = result.scalars().all()
    return users


@router.get('/user_id')
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]) -> User:
    query = select(User).where(User.id == user_id)
    user = db.execute(query).scalar()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')
    return user


@router.post('/create')
async def create_user(user_create: CreateUser, db: Annotated[Session, Depends(get_db)]):
    username_exist = db.execute(select(User).where(User.username == user_create.username)).scalar()
    if username_exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'User {user_create.username} already exist')
    query = insert(User).values(username=user_create.username,
                                firstname=user_create.firstname,
                                lastname=user_create.lastname,
                                age=user_create.age)
    db.execute(query)
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router.put('/update')
async def update_user(user_id: int, user_update: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    user_id_exist = db.execute(select(User).where(User.id == user_id)).scalar()
    if user_id_exist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')
    query = update(User).where(User.id == user_id).values(firstname=user_update.firstname,
                                                          lastname=user_update.lastname,
                                                          age=user_update.age)
    db.execute(query)
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}


@router.delete('/delete')
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user_id_exist = db.execute(select(User).where(User.id == user_id)).scalar()
    if user_id_exist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')
    query = delete(User).where(User.id == user_id)
    db.execute(query)
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}
