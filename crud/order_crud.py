from sqlalchemy.orm import Session
from fastapi import HTTPException
import models

from schemas import order_schemas


def get_orders(db: Session):
    return db.query(models.Order).all()

def get_order_by_id(db: Session, ord_id: int):
    return db.query(models.Order).filter(models.Order.id == ord_id).first()

def create_order(db: Session, ord_data: order_schemas.OrderCreate):
    new_order = models.Order(**ord_data.model_dump())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

def update_order(db: Session, ord_id: int, ord_data: order_schemas.OrderUpdate):
    db_order = db.query(models.Order).filter(models.Order.id == ord_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    for attr, value in ord_data.model_dump(exclude_unset=True).items():
        setattr(db_order, attr, value)
    db.commit()
    return db_order, {"message": "Order updated successfully"} 

def delete_order(db: Session, ord_id: int):
    db.query(models.Order).filter(models.Order.id == ord_id).delete()
    db.commit()
    return {"message": "Order deleted successfully"}
