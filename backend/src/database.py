"""Order service for managing orders.

This module provides functionality for creating and managing orders.
"""
import logging
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


# Models for request/response - matching with database service
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


class OrderStatusUpdate(BaseModel):
    """Model for order status update."""
    status: str


# Health endpoint
@app.get("/health")
def health_check():
    """Health check endpoint to verify service status."""
    return {"status": "healthy"}


@app.post("/orders", response_model=OrderResponse)
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


@app.get("/orders", response_model=List[OrderResponse])
def get_orders(skip: int = 0, limit: int = 100, db = Depends(get_db)):
    """Get a list of orders with pagination."""
    try:
        orders = crud.get_orders(db, skip=skip, limit=limit)
        return orders
    except Exception as e:
        logger.error("Error retrieving orders: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@app.put("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: int, order_status: OrderStatusUpdate, db = Depends(get_db)):
    """Update the status of an order."""
    try:
        db_order = crud.update_order_status(db, order_id=order_id, status=order_status.status)
        if db_order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return db_order
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating order status: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@app.get("/users/{user_id}/orders", response_model=List[OrderResponse])
def get_user_orders(user_id: int, skip: int = 0, limit: int = 100, db = Depends(get_db)):
    """Get all orders for a specific user with pagination."""
    try:
        # Verify user exists
        user = crud.get_user(db, user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        orders = crud.get_user_orders(db, user_id=user_id, skip=skip, limit=limit)
        return orders
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving user orders: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e
