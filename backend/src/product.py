"""Product service for managing products and orders.

This module provides functionality for listing products, searching products,
and creating orders by interacting with the database service.
"""
import logging
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException, Query, Depends, Request
from pydantic import BaseModel

from .services.database import get_db
from .services import crud
from .shared.metrics import setup_metrics
from .shared.auth import authenticate_user, authorize_roles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(title="Product Service")
# Setup Prometheus metrics
setup_metrics(app)


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
    
@app.post("/products", response_model=ProductResponse)
@authenticate_user
@authorize_roles("admin", "superadmin")
def create_product(product: ProductResponse, request: Request, db = Depends(get_db)):
    """Create a new product."""
    try:
        product = crud.create_product(db, product)
        return product
    except Exception as e:
        logger.error("Error creating product: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e

@app.get("/products/user/{user_id}", response_model=List[ProductResponse])
@authenticate_user
def get_user_products(
    user_id: int,
    request: Request,
    db = Depends(get_db)
):
    """Get all products owned by a specific user."""
    try:
        # Get user's orders
        orders = crud.get_user_orders(db, user_id=user_id)
        # Extract products from orders
        products = [order.product for order in orders]
        return products
    except Exception as e:
        logger.error("Error retrieving user products: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e
