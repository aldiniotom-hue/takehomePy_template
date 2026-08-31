from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from routes.auth.auth import (
    create_access_token,
    hash_password,
    verify_password,
)
from routes.models.usersModel import UserModel
from routes.schemas.schemas import BaseUser, Token, UserCreate

router = APIRouter()


@router.post("/create", response_model=BaseUser, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    incomming_user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    response = await db.execute(
        select(UserModel).where(
            func.lower(UserModel.email) == incomming_user.email.lower(),
        )
    )

    existing_user = response.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    new_user = UserModel(
        email=incomming_user.email,
        password_hash=hash_password(incomming_user.password),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    from_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    response = await db.execute(
        select(UserModel).where(
            func.lower(UserModel.email) == from_data.username.lower(),
        )
    )

    existing_user = response.scalars().first()

    if not existing_user or not verify_password(
        from_data.password, existing_user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_min)
    access_token = create_access_token(
        data={"sub": str(existing_user.id)}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")
