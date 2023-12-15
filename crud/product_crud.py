from sqlalchemy.orm import Session
from schemas import product_schemas
from fastapi import HTTPException
import models

def get_products(db: Session):
    return db.query(models.Product).all()

def get_product_by_id(db: Session, prod_id: int):
    return db.query(models.Product).filter(models.Product.id == prod_id).first()

def create_product(db: Session, product_data: product_schemas.ProductCreate):
    new_product = models.Product(**product_data.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

def update_product(db: Session, prod_id: int, product_data: product_schemas.ProductUpdate):
    db_product = db.query(models.Product).filter(models.Product.id == prod_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for attr, value in product_data.model_dump(exclude_unset=True).items():
        setattr(db_product, attr, value)
    db.commit()
    return db_product

def delete_product(db: Session, prod_id: int):
    db.query(models.Product).filter(models.Product.id == prod_id).delete()
    db.commit()
    return {"message": "Product deleted successfully"}