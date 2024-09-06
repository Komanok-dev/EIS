from pydantic import BaseModel


class ApartmentSchema(BaseModel):
    number: int
    square: float


class HouseSchema(BaseModel):
    city: str
    street: str
    number: int


class AddHouseSchema(HouseSchema):
    apartments: list[ApartmentSchema]
