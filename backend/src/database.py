"""
Database service for handling user, product, order and payment operations.
This module provides FastAPI endpoints to interact with the database.
"""
from datetime import date
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .services import crud, models, database


# Initialize FastAPI application
app = FastAPI(title="Database Service")

# Create tables in the database
models.Base.metadata.create_all(bind=database.engine)

# Pydantic models for data validation
class UserBase(BaseModel):
    """Base model for user data validation."""
    username: str

class UserCreate(UserBase):
    """Model for user creation with additional fields."""
    password: str
    role: Optional[str] = "user"

class User(UserBase):
    """Complete user model including database fields."""
    id: int
    role: str

    class Config:  # pylint: disable=R0903
        """Pydantic configuration for ORM mode."""
        orm_mode = True

class ProductBase(BaseModel):
    """Base model for product data validation."""
    title: str
    authors: str
    published_date: date
    description: str
    price: float

class ProductCreate(ProductBase):
    """Model for product creation."""

class Product(ProductBase):
    """Complete product model including database fields."""
    id: int

    class Config:  # pylint: disable=R0903
        """Pydantic configuration for ORM mode."""
        orm_mode = True

class OrderBase(BaseModel):
    """Base model for order data validation."""
    user_id: int
    product_id: int

class OrderCreate(OrderBase):
    """Model for order creation."""

class Order(OrderBase):
    """Complete order model including database fields."""
    id: int
    status: str

    class Config:  # pylint: disable=R0903
        """Pydantic configuration for ORM mode."""
        orm_mode = True

class PaymentBase(BaseModel):
    """Base model for payment data validation."""
    order_id: int
    amount: float

class PaymentCreate(PaymentBase):
    """Model for payment creation."""

class Payment(PaymentBase):
    """Complete payment model including database fields."""
    id: int
    status: str

    class Config:  # pylint: disable=R0903
        """Pydantic configuration for ORM mode."""
        orm_mode = True

# Health endpoint
@app.get("/health")
def health_check():
    """Health check endpoint to verify service status."""
    return {"status": "healthy"}

# User routes
@app.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(database.get_db)):
    """Create a new user if the username is not already registered."""
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, username=user.username, password=user.password, role=user.role)

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(database.get_db)):
    """Get a user by ID."""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Product routes
@app.post("/products/", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(database.get_db)):
    """Create a new product."""
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
    """Get a list of products with pagination."""
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

@app.get("/products/search", response_model=List[Product])
def search_products(
    q: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db)
    ):
    """Search for products by query string with pagination."""
    products = crud.search_products(db, query=q, skip=skip, limit=limit)
    return products

@app.get("/products/{product_id}", response_model=Product)
def read_product(product_id: int, db: Session = Depends(database.get_db)):
    """Get a product by ID."""
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

# Order routes
@app.post("/orders/", response_model=Order)
def create_order(order: OrderCreate, db: Session = Depends(database.get_db)):
    """Create a new order."""
    return crud.create_order(db=db, user_id=order.user_id, product_id=order.product_id)

@app.get("/orders/{order_id}", response_model=Order)
def read_order(order_id: int, db: Session = Depends(database.get_db)):
    """Get an order by ID."""
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.put("/orders/{order_id}/status", response_model=Order)
def update_order_status(order_id: int, status: str, db: Session = Depends(database.get_db)):
    """Update the status of an order."""
    db_order = crud.update_order_status(db, order_id=order_id, status=status)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

# Payment routes
@app.post("/payments/", response_model=Payment)
def create_payment(payment: PaymentCreate, db: Session = Depends(database.get_db)):
    """Create a new payment for an order."""
    return crud.create_payment(db=db, order_id=payment.order_id, amount=payment.amount)

@app.put("/payments/{payment_id}/status", response_model=Payment)
def update_payment_status(payment_id: int, status: str, db: Session = Depends(database.get_db)):
    """Update the status of a payment."""
    db_payment = crud.update_payment_status(db, payment_id=payment_id, status=status)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment
