from fastapi import FastAPI, HTTPException, Depends, Request
from functools import wraps
import os
from dotenv import load_dotenv
import jwt

load_dotenv()

SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES=float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def authenticate_user(func):
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
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.PyJWTError as e:
            print("Error", e)
            raise HTTPException(status_code=401, detail="Invalid token")
    return wrapper

def authorize_roles(*roles):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            user = request.state.user
            if user["role"] not in roles:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, request=request, **kwargs)
        return wrapper
    return decorator