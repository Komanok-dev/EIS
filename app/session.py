from fastapi import Depends
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncIterator
from typing_extensions import Annotated

from app.database import async_engine


def get_async_sessionmaker():
    return sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )


async_sessionmaker = get_async_sessionmaker()


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_sessionmaker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        else:
            await session.commit()
        finally:
            await session.close()


DatabaseSession = Annotated[AsyncSession, Depends(get_session)]
