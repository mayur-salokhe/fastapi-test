from sqlalchemy.orm import Session
from schemas import organization_schemas
from fastapi import HTTPException
import models


def get_organization(db: Session):
    return db.query(models.Organization).all()

def get_organization_by_id(db: Session, org_id: int):
    return db.query(models.Organization).filter(models.Organization.id == org_id).first()

def create_organization(db: Session, org_data: organization_schemas.OrgCreate):
    new_org = models.Organization(**org_data.model_dump())
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    return new_org


def update_organization(db: Session, org_id: int, org_data: organization_schemas.OrgUpdate):
    db_org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if db_org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    for attr, value in org_data.model_dump(exclude_unset=True).items():
        setattr(db_org, attr, value)
    db.commit()
    return {"message": "Organization Updated successfully"}

def delete_organization(db: Session, org_id: int):
    db.query(models.Organization).filter(models.Organization.id == org_id).delete()
    db.commit()
    return {"message": "Organization deleted successfully"}