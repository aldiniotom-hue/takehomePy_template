from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.notificationModel import NotificationModel
from models.usersModel import UserModel
from routes.auth.auth import CurrentUser
from schemas.schemas import NotificationCreate, NotificationPublic

router = APIRouter()


@router.post(
    "/create", response_model=NotificationPublic, status_code=status.HTTP_201_CREATED
)
async def create_notification(
    incoming_notification: NotificationCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(UserModel).where(UserModel.id == current_user.id))

    exusting_user = result.scalars().first()

    if not exusting_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Log in first",
        )

    new_notification = NotificationModel(
        title=incoming_notification.title,
        content=incoming_notification.content,
        channel=incoming_notification.channel,
        owner_id=exusting_user.id,
        notification_creator=exusting_user,
    )

    db.add(new_notification)
    await db.commit()
    await db.refresh(new_notification)

    # send_notification(new_notification)

    return new_notification


@router.patch("/patch/{notification_id}", response_model=NotificationPublic)
async def notification_partial_update(
    notification_id: int,
    notification: NotificationCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(UserModel).where(UserModel.id == current_user.id))

    existing_user = result.scalars().first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Log in first.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(NotificationModel).where(NotificationModel.id == notification_id)
    )

    existing_notification = result.scalars().first()

    if not existing_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No notification found.",
        )
    if existing_user.id != existing_notification.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have no wonership of this notification.",
        )

    updated_data = notification.model_dump(exclude_unset=True)
    for field, value in updated_data.items():
        setattr(existing_notification, field, value)

    await db.commit()
    await db.refresh(existing_notification)

    return existing_notification


@router.delete("/delete/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(UserModel).where(UserModel.id == current_user.id))

    existing_user = result.scalars().first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Log in first.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(NotificationModel).where(NotificationModel.id == notification_id)
    )

    existing_notification = result.scalars().first()

    if not existing_notification:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Post not found",
        )
    if existing_user.id != existing_notification.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have no wonership of this notification.",
        )

    await db.delete(existing_notification)
    await db.commit()


@router.get("/get_all", response_model=list[NotificationPublic])
async def get_all_user_notifications(
    current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(UserModel).where(UserModel.id == current_user.id))

    existing_user = result.scalars().first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Log in first.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(NotificationModel).where(NotificationModel.owner_id == existing_user.id)
    )

    user_notifications = result.scalars()

    if not user_notifications:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="You have no notifications."
        )

    return user_notifications


def send_notification(notification: NotificationModel):
    raise NotImplementedError
