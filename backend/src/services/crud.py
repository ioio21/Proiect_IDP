# database/crud.py
from sqlalchemy.orm import Session
from . import models
from datetime import date
from typing import List, Optional

# Funcții CRUD pentru utilizatori
def create_user(db: Session, username: str, password: str, role: str = "user"):
    """Creează un utilizator nou"""
    db_user = models.User(username=username, password=password, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    """Obține un utilizator după ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    """Obține un utilizator după username"""
    return db.query(models.User).filter(models.User.username == username).first()

# Funcții CRUD pentru produse
def create_product(db: Session, title: str, authors: str, published_date: date, description: str, price: float):
    """Creează un produs nou (lucrare științifică)"""
    db_product = models.Product(
        title=title,
        authors=authors,
        published_date=published_date,
        description=description,
        price=price
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product(db: Session, product_id: int):
    """Obține un produs după ID"""
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    """Obține o listă de produse"""
    return db.query(models.Product).offset(skip).limit(limit).all()

def search_products(db: Session, query: str, skip: int = 0, limit: int = 100):
    """Caută produse după titlu sau autor"""
    search = f"%{query}%"
    return db.query(models.Product).filter(
        (models.Product.title.ilike(search)) | 
        (models.Product.authors.ilike(search)) |
        (models.Product.description.ilike(search))
    ).offset(skip).limit(limit).all()

# Funcții CRUD pentru comenzi
def create_order(db: Session, user_id: int, product_id: int):
    """Creează o comandă nouă"""
    db_order = models.Order(user_id=user_id, product_id=product_id)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_order(db: Session, order_id: int):
    """Obține o comandă după ID"""
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def update_order_status(db: Session, order_id: int, status: str):
    """Actualizează statusul unei comenzi"""
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order:
        db_order.status = status
        db.commit()
        db.refresh(db_order)
    return db_order

# Funcții CRUD pentru plăți
def create_payment(db: Session, order_id: int, amount: float):
    """Creează o plată nouă"""
    db_payment = models.Payment(order_id=order_id, amount=amount)
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def update_payment_status(db: Session, payment_id: int, status: str):
    """Actualizează statusul unei plăți"""
    db_payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if db_payment:
        db_payment.status = status
        db.commit()
        db.refresh(db_payment)
    return db_payment