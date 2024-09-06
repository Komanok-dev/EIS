from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.celery import celery_app
from app.models import House, Apartment, Counter, Payment, Rate
from app.session import async_sessionmaker
import asyncio


@celery_app.task
def calculate_payment_sync(house_id: int, month: int):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(calculate_payment(house_id, month))


async def calculate_payment(house_id: int, month: int):
    async with async_sessionmaker() as session:
        house = (
            await session.execute(
                select(House)
                .where(House.id == house_id)
                .options(
                    selectinload(House.apartments)
                    .selectinload(Apartment.counters)
                )
            )
        ).scalar_one_or_none()

        if not house:
            return {"error": "House not found"}

        rate = (
            await session.execute(select(Rate).limit(1))
        ).scalar_one_or_none()
        if not rate:
            return {"error": "Rate not found"}

        for apartment in house.apartments:
            existing_payment = (
                await session.execute(
                    select(Payment)
                    .where(
                        and_(
                            Payment.apartment_id == apartment.id,
                            Payment.month == month
                        )
                    )
                )
            ).scalar_one_or_none()
            if existing_payment and existing_payment.total:
                continue

            current_counter = (
                await session.execute(
                    select(Counter)
                    .where(
                        and_(
                            Counter.apartment_id == apartment.id,
                            Counter.month == month
                        )
                    )
                )
            ).scalar_one_or_none()

            previous_counter = (
                await session.execute(
                    select(Counter)
                    .where(
                        and_(
                            Counter.apartment_id == apartment.id,
                            Counter.month < month
                        )
                    )
                    .order_by(Counter.month.desc())
                    .limit(1)
                )
            ).scalar_one_or_none()

            if not current_counter or not previous_counter:
                continue

            water_consumption = current_counter.value - previous_counter.value
            water_cost = water_consumption * rate.water

            maintenance_cost = apartment.square * rate.maintenance

            total_cost = water_cost + maintenance_cost

            payment = Payment(
                apartment_id=apartment.id,
                month=month,
                water_cost=water_cost,
                maintenance_cost=maintenance_cost,
                total=total_cost
            )
            session.add(payment)
        await asyncio.sleep(30)
        await session.commit()

        return {
            "ok": True,
            "detail": f"Payment calculated and saved for all apartments of {house.address}"
        }
