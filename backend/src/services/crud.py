"""CRUD operations for database models."""

from sqlalchemy.orm import Session

from . import models

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
def get_product(db: Session, product_id: int):
    """Obține un produs după ID"""
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    """Obține o listă de produse"""
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product):
    """Creează un produs nou"""
    db_product = models.Product(id=product.id, title=product.title, authors=product.authors, published_date=product.published_date, description=product.description, price=product.price, quantity=product.quantity)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Funcții CRUD pentru comenzi
def create_order(db: Session, user_id: int, product_id: int):
    """Creează o comandă nouă"""
    db_order = models.Order(user_id=user_id, product_id=product_id, status="created")
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_order(db: Session, order_id: int):
    """Obține o comandă după ID"""
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def get_orders(db: Session):
    """Obține toate comenzile"""
    return db.query(models.Order).all()

def get_user_orders(db: Session, user_id: int):
    """Obține comenzile unui utilizator"""
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()