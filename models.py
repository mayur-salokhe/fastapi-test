from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base
from sqlalchemy import Enum as SQLEnum
from enum import Enum


class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String) 
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String,unique=True)
    country_code = Column(String)
    password = Column(String) 
    gender = Column(SQLEnum(GenderEnum),nullable=False)
    is_active = Column(Boolean,default=True)

    order_relation = relationship("Order", back_populates="user_relation")
    address_relation = relationship("Address",back_populates="user_relation")
    organization_relation = relationship("Organization",secondary="role",back_populates="user_relation")
    

class Organization(Base):
    __tablename__ = "organization"

    id = Column(Integer, primary_key=True)
    org_name = Column(String,unique=True)

    order_relation = relationship("Order", back_populates="organization_relation")
    user_relation = relationship("User",secondary="role",back_populates="organization_relation")

class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    org_id = Column(Integer, ForeignKey("organization.id"))
    role = Column(String)
    

class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    prod_name = Column(String,unique=True)
    prod_og_price = Column(Numeric)
    prod_new_price = Column(Numeric)
    prod_desc = Column(Text)
    prod_image = Column(ARRAY(String)) 
    prod_thumb_img = Column(ARRAY(String)) 

    order_relation = relationship("Order", back_populates="product_relation")

class Order(Base):
    __tablename__ = "order"

    id = Column(Integer,primary_key=True)
    prod_id = Column(Integer, ForeignKey("product.id"))
    ord_date = Column(DateTime)
    org_id = Column(Integer, ForeignKey("organization.id"))
    ord_price = Column(Numeric)
    user_id = Column(Integer,ForeignKey("user.id"))

    user_relation = relationship("User",back_populates="order_relation")
    organization_relation = relationship("Organization",back_populates="order_relation")
    product_relation = relationship("Product",back_populates="order_relation")
    

class Address(Base):
    __tablename__ = "address"

    id = Column(Integer,primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    address_line1 = Column(Text)
    address_line2 = Column(Text)
    city = Column(String)
    postal_code = Column(Integer)
    state = Column(String)
    country = Column(String)

    user_relation = relationship("User",back_populates="address_relation")

