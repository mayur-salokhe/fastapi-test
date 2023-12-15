from pydantic import BaseModel
from typing import List


class AddressBase(BaseModel):
    address_line1: str
    address_line2: str
    city: str
    postal_code: int
    state: str
    country: str

class AddressCreate(AddressBase):
    pass

class AddressUpdate(AddressBase):
    pass

class AddressRead(AddressBase):
    id: int

    class Config:
        from_attributes = True
