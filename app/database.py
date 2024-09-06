from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


from app.models import Base
from app.settings import database_settings


async_engine: AsyncEngine = create_async_engine(
    database_settings.url,
    echo=True
)


async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
