from fastapi import APIRouter, Depends
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from typing import Annotated

from app.celery import celery_app
from app.session import DatabaseSession
from app.schemas import HouseSchema, AddHouseSchema
from app.models import House, Apartment
from app.calculations import calculate_payment_sync


router = APIRouter(prefix="", tags=["Houses"])


@router.get("/")
async def get_house(
    house: Annotated[HouseSchema, Depends()], session: DatabaseSession
):
    result = (
        await session.execute(
            select(House)
            .where(
                and_(
                    House.city == house.city,
                    House.street == house.street,
                    House.number == house.number
                )
            )
            .options(joinedload(House.apartments))
        )
    ).unique().scalar_one_or_none()
    if result:
        return {
            "ok": True,
            "address": result.address,
            "apartments": result.apartments
        }
    return {"ok": True, "detail": "not found"}


@router.post("/add_house")
async def add_house(
    house: Annotated[AddHouseSchema, Depends()], session: DatabaseSession
):
    new_house = House(
        city=house.city,
        street=house.street,
        number=house.number
    )
    session.add(new_house)
    await session.flush()

    for apartment in house.apartments:
        new_apartment = Apartment(
            number=apartment.number,
            square=apartment.square,
            house_id=new_house.id
        )
        session.add(new_apartment)

    return {"ok": True, "house added": new_house.address}


@router.get('/count_payment')
async def count_payment(house_id: int, month: int):
    result = calculate_payment_sync.delay(house_id, month)
    return {"task_id": result.id}


@router.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    return {"task_id": task_id, "status": result.status, "result": result.result}
