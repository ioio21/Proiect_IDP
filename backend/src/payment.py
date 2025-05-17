"""Payment service."""

from fastapi import FastAPI, HTTPException, Body, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
from .services.database import get_db
from .services import crud
from .shared.auth import authenticate_user

app = FastAPI()

class PaymentResponse(BaseModel):
    oder_id: int
    amount: float
    
@app.post("/{oder_id}/pay")
@authenticate_user
def pay_order(order_id: int, request: Request, db = Depends(get_db)):
    """Pay for an order."""
    try:
        order = crud.get_order(db, order_id=order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        user = crud.get_user_by_username(db, username=request.state.user["username"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.id != order.user_id:
            raise HTTPException(status_code=403, detail="User is not the owner of the order")
        status = crud.set_order_status(db, order_id=order_id, status="paid")
        if not status:
            raise HTTPException(status_code=404, detail="Order not found")
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e
