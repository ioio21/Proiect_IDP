# database/app.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from .services import crud, models, database
from pydantic import BaseModel
from datetime import date


# Inițializare aplicație FastAPI
app = FastAPI(title="Database Service")

# Creare tabele în baza de date
models.Base.metadata.create_all(bind=database.engine)

# Modele Pydantic pentru validarea datelor
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "user"

class User(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    title: str
    authors: str
    published_date: date
    description: str
    price: float

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    user_id: int
    product_id: int

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    status: str

    class Config:
        orm_mode = True

class PaymentBase(BaseModel):
    order_id: int
    amount: float

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: int
    status: str

    class Config:
        orm_mode = True

# Endpoint de sănătate
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Rute pentru utilizatori
@app.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, username=user.username, password=user.password, role=user.role)

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(database.get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Rute pentru produse
@app.post("/products/", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(database.get_db)):
    return crud.create_product(
        db=db, 
        title=product.title,
        authors=product.authors,
        published_date=product.published_date,
        description=product.description,
        price=product.price
    )

@app.get("/products/", response_model=List[Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

@app.get("/products/search", response_model=List[Product])
def search_products(q: str, skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    products = crud.search_products(db, query=q, skip=skip, limit=limit)
    return products

@app.get("/products/{product_id}", response_model=Product)
def read_product(product_id: int, db: Session = Depends(database.get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

# Rute pentru comenzi
@app.post("/orders/", response_model=Order)
def create_order(order: OrderCreate, db: Session = Depends(database.get_db)):
    return crud.create_order(db=db, user_id=order.user_id, product_id=order.product_id)

@app.get("/orders/{order_id}", response_model=Order)
def read_order(order_id: int, db: Session = Depends(database.get_db)):
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.put("/orders/{order_id}/status", response_model=Order)
def update_order_status(order_id: int, status: str, db: Session = Depends(database.get_db)):
    db_order = crud.update_order_status(db, order_id=order_id, status=status)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

# Rute pentru plăți
@app.post("/payments/", response_model=Payment)
def create_payment(payment: PaymentCreate, db: Session = Depends(database.get_db)):
    return crud.create_payment(db=db, order_id=payment.order_id, amount=payment.amount)

@app.put("/payments/{payment_id}/status", response_model=Payment)
def update_payment_status(payment_id: int, status: str, db: Session = Depends(database.get_db)):
    db_payment = crud.update_payment_status(db, payment_id=payment_id, status=status)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment