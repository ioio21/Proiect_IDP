"""Order service for managing orders.

This module provides functionality for creating and managing orders.
"""
import logging
from typing import List

from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel

from .services.database import get_db
from .services import crud
from .shared.metrics import setup_metrics
from .shared.auth import authenticate_user, authorize_roles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(title="Order Service")
# Setup Prometheus metrics
setup_metrics(app)


class BaseConfig:
    """Base Pydantic configuration."""
    orm_mode = True


# Models for request/response
class OrderRequest(BaseModel):
    """Order request model for creating a new order."""
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
@authenticate_user
async def create_order(order: OrderRequest, request: Request, db = Depends(get_db)):
    """Create a new order for a product."""
    try:
        # Get the authenticated user
        user = crud.get_user_by_username(db, username=request.state.user["username"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verify that the product exists
        product = crud.get_product(db, product_id=order.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Create the order
        new_order = crud.create_order(db=db, user_id=user.id, product_id=order.product_id)
        return new_order
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error("Error creating order: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@app.get("/orders", response_model=List[OrderResponse])
@authenticate_user
@authorize_roles("admin", "superadmin")
async def get_orders(request: Request, db = Depends(get_db)):
    """Get a list of all orders. Requires admin privileges."""
    try:
        orders = crud.get_orders(db)
        return orders
    except Exception as e:
        logger.error("Error retrieving orders: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@app.get("/orders/{order_id}", response_model=OrderResponse)
@authenticate_user
async def get_order(order_id: int, request: Request, db = Depends(get_db)):
    """Get an order by ID. Users can only view their own orders unless they are admin."""
    try:
        db_order = crud.get_order(db, order_id=order_id)
        if db_order is None:
            raise HTTPException(status_code=404, detail="Order not found")

        # Get the authenticated user
        user = crud.get_user_by_username(db, username=request.state.user["username"])
        
        # Check if user is admin or the order owner
        if user.role not in ["admin", "superadmin"] and db_order.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this order")

        return db_order
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving order: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@app.get("/users/{username}/orders", response_model=List[OrderResponse])
@authenticate_user
async def get_user_orders(username: str, request: Request, db = Depends(get_db)):
    """Get all orders for a specific user. Users can only view their own orders unless they are admin."""
    try:
        # Get the authenticated user
        auth_user = crud.get_user_by_username(db, username=request.state.user["username"])
        
        # Get the target user
        target_user = crud.get_user_by_username(db, username=username)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Check if user is admin or viewing their own orders
        if auth_user.role not in ["admin", "superadmin"] and auth_user.username != username:
            raise HTTPException(status_code=403, detail="Not authorized to view these orders")
            
        orders = crud.get_user_orders(db, user_id=target_user.id)
        return orders
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving user orders: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e