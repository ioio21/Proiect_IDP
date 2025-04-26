"""Order service for managing orders.

This module provides functionality for creating and managing orders.
"""
import logging
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

from .services.database import get_db
from .services import crud

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(title="Order Service")


class BaseConfig:
    """Base Pydantic configuration."""
    orm_mode = True


# Models for request/response
class OrderRequest(BaseModel):
    """Order request model for creating a new order."""
    user_id: int
    product_id: int


class OrderResponse(BaseModel):
    """Order response model returned after order creation."""
    id: int
    user_id: int
    product_id: int
    status: str

    class Config(BaseConfig):
        """Pydantic configuration."""
        pass


# Health endpoint
@app.get("/health")
def health_check():
    """Health check endpoint to verify service status."""
    return {"status": "healthy"}


@app.post("/orders", response_model=OrderResponse, status_code=201)
def create_order(order: OrderRequest, db = Depends(get_db)):
    """Create a new order for a product."""
    try:
        # Verify that the product exists
        product = crud.get_product(db, product_id=order.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Verify that the user exists
        user = crud.get_user(db, user_id=order.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create the order
        new_order = crud.create_order(db=db, user_id=order.user_id, product_id=order.product_id)
        return new_order
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error("Error creating order: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@app.get("/orders", response_model=List[OrderResponse])
def get_orders(db = Depends(get_db)):
    """Get a list of all orders."""
    try:
        orders = crud.get_orders(db)
        return orders
    except Exception as e:
        logger.error("Error retrieving orders: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db = Depends(get_db)):
    """Get an order by ID."""
    try:
        db_order = crud.get_order(db, order_id=order_id)
        if db_order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return db_order
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving order: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@app.get("/users/{user_id}/orders", response_model=List[OrderResponse])
def get_user_orders(user_id: int, db = Depends(get_db)):
    """Get all orders for a specific user."""
    try:
        # Verify user exists
        user = crud.get_user(db, user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        orders = crud.get_user_orders(db, user_id=user_id)
        return orders
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving user orders: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e
