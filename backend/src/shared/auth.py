"""Authentication and authorization utilities for the application."""
import os
from functools import wraps

from dotenv import load_dotenv
from fastapi import HTTPException, Request
from pydantic import BaseModel
import jwt

load_dotenv()

SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES=float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

class User(BaseModel):
    """User model with role information."""
    username: str
    password: str
    role: str

class UserWithoutRole(BaseModel):
    """User model without role information for registration."""
    username: str
    password: str

class TokenSchema(BaseModel):
    """Schema for token response."""
    token: str
    token_type: str

def authenticate_user(func):
    """Decorator to authenticate users from JWT token in request headers."""
    @wraps(func)
    async def wrapper(*args, request: Request, **kwargs):
        token = request.headers.get("Authorization")

        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")

        token = token.split("Bearer ")[1]

        try:
            payload = jwt.decode(token.encode(), SECRET_KEY.encode(), algorithms=[ALGORITHM])
            request.state.user = {
                "username": payload.get("sub"),
                "role": payload.get("role")
            }
            return await func(*args, request=request, **kwargs)
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(status_code=401, detail="Token expired") from exc
        except jwt.PyJWTError as e:
            print("Error", e)
            raise HTTPException(status_code=401, detail="Invalid token") from e
    return wrapper

def authorize_roles(*roles):
    """Decorator to check if authenticated user has required role."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            user = request.state.user
            if user["role"] not in roles:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, request=request, **kwargs)
        return wrapper
    return decorator
