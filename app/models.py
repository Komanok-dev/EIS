from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base

from app.enum import CounterType


Base = declarative_base()


class House(Base):
    __tablename__ = "house"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    city: Mapped[str]
    street: Mapped[str]
    number: Mapped[int]
    apartments: Mapped[list["Apartment"]] = relationship(
        "Apartment", back_populates="house"
    )

    @property
    def address(self) -> str:
        return f"{self.city}, {self.street}, {self.number}"


class Apartment(Base):
    __tablename__ = "apartment"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    number: Mapped[int]
    square: Mapped[float]
    house_id: Mapped[int] = mapped_column(ForeignKey("house.id"))
    house: Mapped["House"] = relationship("House", back_populates="apartments")
    counters: Mapped[list["Counter"]] = relationship(
        "Counter", back_populates="apartment"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="apartment"
    )

    @property
    def address(self) -> str:
        return f"{self.house.address} - {self.number}"


class Counter(Base):
    __tablename__ = "counter"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[CounterType] = mapped_column(Enum(CounterType))
    value: Mapped[float]
    month: Mapped[int]
    apartment_id: Mapped[int] = mapped_column(ForeignKey("apartment.id"))
    apartment: Mapped["Apartment"] = relationship(
        "Apartment", back_populates="counters"
    )


class Rate(Base):
    __tablename__ = "rate"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    water: Mapped[float]
    maintenance: Mapped[float]


class Payment(Base):
    __tablename__ = "payment"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    apartment_id: Mapped[int] = mapped_column(ForeignKey("apartment.id"))
    apartment: Mapped["Apartment"] = relationship(
        "Apartment", back_populates="payments"
    )
    month: Mapped[int]
    water_cost: Mapped[float]
    maintenance_cost: Mapped[float]
    total: Mapped[float]
