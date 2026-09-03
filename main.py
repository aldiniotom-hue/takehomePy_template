from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import engine
from routes.APIHealthTest import APIHealthTestController
from routes.notifications import notificationController
from routes.users import usersController


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)


app.include_router(
    APIHealthTestController.router, prefix="/api/healthtest", tags=["APIHealthTest"]
)
app.include_router(usersController.router, prefix="/api/users", tags=["users"])
app.include_router(
    notificationController.router, prefix="/api/notifications", tags=["notifications"]
)
