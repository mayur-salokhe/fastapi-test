from sqlalchemy.orm import Session
from fastapi import HTTPException
import models

from schemas import address_schemas


def get_addresses(db: Session):
    return db.query(models.Address).all()

def get_address_by_id(db: Session, address_id: int):
    return db.query(models.Address).filter(models.Address.id == address_id).first()

def create_address(db: Session, address_data: address_schemas.AddressCreate):
    new_address = models.Address(**address_data.model_dump())
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address


def update_address(db: Session, address_id: int, address_data: address_schemas.AddressUpdate):
    db_address = db.query(models.Address).filter(models.Address.id == address_id).first()
    if db_address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    for attr, value in address_data.model_dump(exclude_unset=True).items():
        setattr(db_address, attr, value)
    db.commit()
    return db_address, {"message": "Address updated successfully"} 

def delete_address(db: Session, address_id: int):
    db.query(models.Address).filter(models.Address.id == address_id).delete()
    db.commit()
    return {"message": "Address deleted successfully"}
