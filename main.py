from fastapi import Depends, FastAPI, HTTPException,status
from sqlalchemy.orm import Session
from typing import Annotated, List
import models
from database import SessionLocal, engine
from crud import user_crud,product_crud,address_crud,order_crud,organization_crud,role_crud
from schemas import user_schemas,product_schemas,address_schemas,order_schemas,organization_schemas, role_schemas
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# openssl rand -hex 32
SECRET_KEY = "0b23f983d10e82a45165fa5abbdbc1ed2be224fdd8652567862daeeef75e82b2"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

class Hasher():
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

""" def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password) """

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str):
    #user = user_crud.get_user(db, username)
    user = db.query(models.User).filter(models.User.username == username).first() 
    if not user:
        return False
    if not Hasher.verify_password(password, user.password):
        return False
    return user



async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},    
	)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = user_crud.get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user



@app.post("/users/create/", response_model=user_schemas.UserCreate)
def create_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    db_user_by_username = user_crud.get_user(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = Hasher.get_password_hash(user.password)

    user_data = user.model_dump()
    user_data['password'] = hashed_password

    db_user = user_crud.create_user(db=db, user=user_schemas.UserCreate(**user_data))
    return db_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/", response_model=List[user_schemas.UserRead])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = user_crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/me/", response_model=user_schemas.UserRead)
async def read_users_me(
    current_user: Annotated[user_schemas.UserBase, Depends(get_current_user)]
):
    return current_user


@app.put("/users/update/{user_id}")
def update_user(user_id: int, user: user_schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    for attr, value in user.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(db_user, attr, value)

    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/users/delete/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"Message":"User ID {user_id} Deleted "}



@app.get("/addresses/", response_model=list[address_schemas.AddressRead])
def read_addresses(db: Session = Depends(get_db)):
    db_address = address_crud.get_addresses(db)
    return db_address

@app.get("/addresses/{address_id}", response_model=address_schemas.AddressRead)
def read_address(address_id: int, db: Session = Depends(get_db)):
    address = address_crud.get_address_by_id(db, address_id)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

@app.post("/addresses/", response_model=address_schemas.AddressCreate)
def create_new_address(address_data: address_schemas.AddressCreate, db: Session = Depends(get_db)):
    return address_crud.create_address(db, address_data)



@app.put("/addresses/{address_id}", response_model=address_schemas.AddressRead)
async def update_existing_address(
    address_id: int, address_data: address_schemas.AddressUpdate, db: Session = Depends(get_db)
):
    return address_crud.update_address(db, address_id, address_data)

@app.delete("/addresses/{address_id}")
def delete_existing_address(address_id: int, db: Session = Depends(get_db)):
    address = address_crud.get_address_by_id(db, address_id)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return address_crud.delete_address(db, address_id)


@app.get("/organizations/", response_model=list[organization_schemas.OrgRead])
def read_organizations(db: Session = Depends(get_db)):
    db_org = organization_crud.get_organization(db)
    return db_org

@app.get("/organizations/{org_id}", response_model=organization_schemas.OrgRead)
def read_organization_by_id(org_id: int, db: Session = Depends(get_db)):
    organization = organization_crud.get_organization_by_id(db, org_id)
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization

@app.post("/create_organization/", response_model=organization_schemas.OrgCreate)
def create_new_organization(org_data: organization_schemas.OrgCreate, db: Session = Depends(get_db)):
    return organization_crud.create_organization(db, org_data)

@app.put("/update_organization/{org_id}")
def update_existing_organization(org_id: int, org_data:organization_schemas.OrgUpdate, db: Session = Depends(get_db)):
    organization = organization_crud.get_organization_by_id(db, org_id)
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization_crud.update_organization(db, org_id, org_data)

@app.delete("/delete_organization/{org_id}")
def delete_existing_organization(org_id: int, db: Session = Depends(get_db)):
    organization = organization_crud.get_organization_by_id(db, org_id)
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization_crud.delete_organization(db, org_id)


@app.post("/create_product/", response_model=product_schemas.ProductCreate)
def create_new_product(product_data: product_schemas.ProductCreate, db: Session = Depends(get_db)):
    return product_crud.create_product(db, product_data)

@app.get("/products/", response_model=list[product_schemas.ProductRead])
def read_products(db: Session = Depends(get_db)):
    db_prod = product_crud.get_products(db)
    return db_prod

@app.get("/products/{prod_id}", response_model=product_schemas.ProductRead)
def read_product_by_id(prod_id: int, db: Session = Depends(get_db)):
    product = product_crud.get_product_by_id(db, prod_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/update_product/{prod_id}")
def update_existing_product(prod_id: int, prod_data:product_schemas.ProductUpdate, db: Session = Depends(get_db)):
    product = product_crud.get_product_by_id(db, prod_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_crud.update_product(db, prod_id, prod_data)



@app.delete("/delete_product/{prod_id}")
def delete_existing_product(prod_id: int, db: Session = Depends(get_db)):
    product = product_crud.get_product_by_id(db, prod_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_crud.delete_product(db, prod_id)



@app.get("/orders/", response_model=list[order_schemas.OrderRead])
def read_orders(db: Session = Depends(get_db)):
    db_order = order_crud.get_orders(db)
    return db_order

@app.get("/orders/{order_id}", response_model=order_schemas.OrderRead)
def read_order_by_id(order_id: int, db: Session = Depends(get_db)):
    order = order_crud.get_order_by_id(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/create_order/", response_model=order_schemas.OrderCreate)
def create_new_order(order_data: order_schemas.OrderCreate, db: Session = Depends(get_db)):
    return order_crud.create_order(db, order_data)

@app.put("/update_order/{order_id}")
def update_existing_order(order_id: int, order_data: order_schemas.OrderUpdate, db: Session = Depends(get_db)):
    order = order_crud.get_order_by_id(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_crud.update_order(db, order_id, order_data)

@app.delete("/delete_order/{order_id}")
def delete_existing_order(order_id: int, db: Session = Depends(get_db)):
    order = order_crud.get_order_by_id(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_crud.delete_order(db, order_id)

@app.get("/roles/", response_model=list[role_schemas.RoleRead])
def read_roles(db: Session = Depends(get_db)):
    db_role = role_crud.get_roles(db)
    return db_role

@app.get("/roles/{role_id}", response_model=role_schemas.RoleRead)
def read_role_by_id(role_id: int, db: Session = Depends(get_db)):
    role = role_crud.get_role_by_id(db, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@app.post("/create_role/", response_model=role_schemas.RoleCreate)
def create_new_role(role_data: role_schemas.RoleCreate, db: Session = Depends(get_db)):
    return role_crud.create_role(db, role_data)

@app.put("/update_role/{role_id}")
def update_existing_role(role_id: int, role_data: role_schemas.RoleUpdate, db: Session = Depends(get_db)):
    role = role_crud.get_role_by_id(db, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role_crud.update_role(db, role_id, role_data)

@app.delete("/delete_role/{role_id}")
def delete_existing_role(role_id: int, db: Session = Depends(get_db)):
    role = role_crud.get_role_by_id(db, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role_crud.delete_role(db, role_id)

