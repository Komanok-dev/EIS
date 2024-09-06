from fastapi import FastAPI

from app.database import create_tables
from app.endpoints import router


async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router)
