from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import engine
from routes.APIHealthTest import APIHealthTestController


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)


app.include_router(
    APIHealthTestController.router, prefix="/api/healthtest", tags=["APIHealthTest"]
)
