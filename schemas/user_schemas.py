from pydantic import BaseModel, EmailStr
from typing import List, Optional 

class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    country_code: str
    phone: str
    gender: str
    
    
class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class UserUpdate(UserBase):
    password: str




    