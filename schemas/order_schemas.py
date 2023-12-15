from pydantic import BaseModel
from typing import List
from datetime import datetime

class OrderBase(BaseModel):
	prod_id: int
	org_date: datetime
	org_id: int
	ord_price: float
	user_id: int

class OrderCreate(OrderBase):
	pass

class OrderUpdate(OrderBase):
	pass

class OrderRead(OrderBase):
	id: int
	
	class Config:
		from_attributes = True