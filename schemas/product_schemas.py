from pydantic import BaseModel
from typing import List

class ProductBase(BaseModel):
    prod_name: str
    prod_og_price: float
    prod_new_price: float
    prod_desc: str
    prod_image: List[str]
    prod_thumb_img: List[str]

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: int

    class Config:
        from_attributes = True
