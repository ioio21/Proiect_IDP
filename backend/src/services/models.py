"""Database models for the services module."""
import datetime

from sqlalchemy import Column, Integer, String, Float, Text, Date, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class User(Base): # pylint: disable=R0903
    """User model representing application users with
    authentication details and role information."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user")

    orders = relationship("Order", back_populates="user")


class Product(Base): # pylint: disable=R0903
    """Product model representing scientific papers available for purchase."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    authors = Column(String)
    published_date = Column(Date, default=datetime.date.today)
    description = Column(Text)
    price = Column(Float)

    orders = relationship("Order", back_populates="product")


class Order(Base): # pylint: disable=R0903
    """Order model tracking purchases made by users."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    status = Column(String, default="created")

    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    payment = relationship("Payment", back_populates="order", uselist=False)


class Payment(Base): # pylint: disable=R0903
    """Payment model tracking financial transactions for orders."""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True)
    amount = Column(Float)
    status = Column(String, default="pending")

    order = relationship("Order", back_populates="payment")
