# database/models.py
from sqlalchemy import Column, Integer, String, Float, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
import datetime

# Tabel pentru utilizatori (dacă nu există deja în serviciul de autentificare)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # Parola hashată
    role = Column(String, default="user")  # roluri: user, admin, superadmin
    
    # Relație cu comenzile
    orders = relationship("Order", back_populates="user")

# Tabel pentru produse (lucrări științifice)
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    authors = Column(String)
    published_date = Column(Date, default=datetime.date.today)
    description = Column(Text)
    price = Column(Float)
    
    # Relație cu comenzile
    orders = relationship("Order", back_populates="product")

# Tabel pentru comenzi
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    status = Column(String, default="created")  # created, paid, delivered
    
    # Relații
    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    payment = relationship("Payment", back_populates="order", uselist=False)

# Tabel pentru plăți
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True)
    amount = Column(Float)
    status = Column(String, default="pending")  # pending, completed, failed
    
    # Relație
    order = relationship("Order", back_populates="payment")