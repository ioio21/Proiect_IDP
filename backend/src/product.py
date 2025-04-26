"""Product service for managing products and orders.

This module provides functionality for listing products, searching products,
and creating orders by interacting with the database service.
"""
import logging
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel

from .services.database import get_db
from .services import crud

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(title="Product Service")


class BaseConfig:
    """Base Pydantic configuration."""
    orm_mode = True


# Models for request/response
class ProductResponse(BaseModel):
    """Product model representing a publication item."""
    id: int
    title: str
    authors: str
    published_date: str
    description: str
    price: float

    class Config(BaseConfig):
        """Pydantic configuration."""


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


@app.get("/health")
def health_check():
    """Health check endpoint to verify service status."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/products", response_model=List[ProductResponse])
def get_products(skip: int = 0, limit: int = 100, db = Depends(get_db)):
    """Get all available products."""
    try:
        products = crud.get_products(db, skip=skip, limit=limit)
        return products
    except Exception as e:
        logger.error("Error retrieving products: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@app.get("/products/search", response_model=List[ProductResponse])
def search_products(
    q: str = Query(..., description="Search query"),
    skip: int = 0,
    limit: int = 100,
    db = Depends(get_db)
):
    """Search for products by title, author, or description."""
    try:
        products = crud.search_products(db, query=q, skip=skip, limit=limit)
        return products
    except Exception as e:
        logger.error("Error searching products: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


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
        new_order = crud.create_order(db, user_id=order.user_id, product_id=order.product_id)
        return new_order
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error("Error creating order: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e
