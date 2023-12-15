from sqlalchemy.orm import Session
from fastapi import HTTPException
import models

from schemas import role_schemas


def get_roles(db: Session):
    return db.query(models.Role).all()

def get_role_by_id(db: Session, role_id: int):
    return db.query(models.Role).filter(models.Role.id == role_id).first()

def create_role(db: Session, role_data: role_schemas.RoleCreate):
    new_role = models.Role(**role_data.model_dump())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


def update_role(db: Session, role_id: int, role_data: role_schemas.RoleUpdate):
    db_role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    for attr, value in role_data.model_dump(exclude_unset=True).items():
        setattr(db_role, attr, value)
    db.commit()
    return db_role, {"message": "Role updated successfully"} 

def delete_role(db: Session, role_id: int):
    db.query(models.Role).filter(models.Role.id == role_id).delete()
    db.commit()
    return {"message": "Role deleted successfully"}
