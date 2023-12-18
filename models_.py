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
    first_name = Column(String)
    last_name = Column(String)
    gender = Column(SQLEnum(GenderEnum),nullable=False)
    email = Column(String, unique=True)
    country_code = Column(String)
    phone = Column(String,unique=True)
    password = Column(String) #temp. 
    is_active = Column(Boolean,default=True)

    order_relation = relationship("Order", back_populates="user_relation")
    address_relation = relationship("Address",back_populates="user_relation")
    organization_relation = relationship("Organization",secondary="role",back_populates="user_relation")

class User_Address(Base):
    __tablename__ = "user_address"

    user_id = Column(Integer,ForeignKey("user.id"))
    address_id = Column(Integer,ForeignKey("address.id"))

class Address(Base):
    __tablename__ = "address"

    id = Column(Integer,primary_key=True)
    address_line1 = Column(Text)
    address_line2 = Column(Text)
    city = Column(String)
    postal_code = Column(Integer)
    state = Column(String)
    country_id = Column(Integer,ForeignKey("countries.id"))

    user_relation = relationship("User",back_populates="address_relation")

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer,primary_key=True)
    country_name = Column(String)


class Organization(Base):
    __tablename__ = "organization"

    id = Column(Integer, primary_key=True)
    org_name = Column(String,unique=True)

    token_relation = relationship("Token",back_populates="organization_relation")
    order_relation = relationship("Order", back_populates="organization_relation")
    user_relation = relationship("User",secondary="role",back_populates="organization_relation")

class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    org_id = Column(Integer, ForeignKey("organization.id"))
    role = Column(String)
    
class Token(Base):
    __tablename__ = "token"

    id = Column(Integer,primary_key=True)
    token_key = Column(String)
    validity = Column(DateTime)
    org_id = Column(Integer,ForeignKey("organization.id"))
    is_active = Column(Boolean, default = True) #For spam/multiple request 

    organization_relation = relationship("organization",back_populates="token_relation")


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
    #prod_id = Column(Integer, ForeignKey("product.id"))
    ord_date = Column(DateTime)
    org_id = Column(Integer, ForeignKey("organization.id"))
    ord_price = Column(Numeric)
    user_id = Column(Integer,ForeignKey("user.id"))
    payment_method_id = Column(Integer,ForeignKey("user_payment_method.id"))
    shipping_address_id = Column(Integer,ForeignKey("address.id"))
    total_orders = Column(Integer)
    order_status = Column(String,ForeignKey("order_status.id"))

    
    user_relation = relationship("User",back_populates="order_relation")
    organization_relation = relationship("Organization",back_populates="order_relation")
    product_relation = relationship("Product",back_populates="order_relation")
    payment_method_relation = relationship("UserPaymentMethod")
    address_relation = relationship("Address")
    order_relation = relationship("Order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer,primary_key=True)
    ord_id = Column(Integer, ForeignKey("order.id"))
    prod_id = Column(Integer,ForeignKey("product.id"))
    quantity = Column(Integer)  

class OrderStatus(Base):
    __tablename__ = "order_status"

    id = Column(Integer,primary_key=True)
    status = Column(String)

    
class UserPaymentMethod(Base):
    __tablename__ = "user_payment_method"
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey("user.id"))
    payment_type_id = Column(Integer,ForeignKey("payment_type.id"))
    #account_number = Column(String)
    #expiry_date = Column(DateTime)
    is_default = Column(Boolean)

    #user_relation = relationship("User",back_populates="user_payment_relation")
    #payment_type_relation = relationship("PaymentType",back_populates="user_payment_relation")

class PaymentType(Base):
    __tablename__ = "payment_type"
    id = Column(Integer,primary_key=True)
    value = Column(String)


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer,primary_key=True)
    coupon_name = Column(String)
    code = Column(String)
    discount_percentage = Column(Integer)
    expiry_date = Column(DateTime)
    is_active = Column(Boolean)
    usage_limit = Column(Integer)
    is_private = Column(Boolean)



