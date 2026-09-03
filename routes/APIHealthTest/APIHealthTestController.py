from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.apiHealthModel import APIHealthTestModel
from schemas.schemas import APIHealthBase

router = APIRouter()


@router.get("/getHealthTest", response_model=APIHealthBase)
async def get_last_health_test(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(APIHealthTestModel))
    # .order_by(desc(APIHealthTestModel.datetime))
    test = result.scalars().first()

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No test ran yet."
        )

    return test


@router.post("/postHealthTest", status_code=status.HTTP_201_CREATED)
async def post_health_test(
    test: APIHealthBase, db: Annotated[AsyncSession, Depends(get_db)]
):
    new_test = APIHealthTestModel(message=test.message)

    db.add(new_test)
    await db.commit()
    await db.refresh(new_test)

    return new_test
