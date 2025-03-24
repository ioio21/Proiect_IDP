# Authentification service
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC
from dotenv import load_dotenv
from functools import wraps
import os
import jwt

load_dotenv()

SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES=float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Fake database. To be removed
fake_db = {
    "admin": {
        "password": hash_password("admin"),
        "role": "admin",
    }
}

class User(BaseModel):
    username: str
    password: str
    role: str
    
class UserWithoutRole(BaseModel):
    username: str
    password: str

class TokenSchema(BaseModel):
    token: str
    token_type: str

def create_jwt_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY.encode(), ALGORITHM)

# User registration
@app.post("/register/")
async def register(user: UserWithoutRole) -> dict:
    if user.username in fake_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    fake_db[user.username] = {
        "password": hash_password(user.password),
        "role": "user"
    }
    return {"message": "User registered successfully"}

# User login
@app.post("/login/", response_model=TokenSchema)
async def login(user: UserWithoutRole) -> dict:
    if user.username not in fake_db or not verify_password(user.password, fake_db[user.username]["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    role = fake_db[user.username]["role"]
    token = create_jwt_token({"sub": user.username, "role": role}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"token": token, "token_type": "bearer"}

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

# This is an example of a protected endpoint that needs authentication
@app.get("/protected/")
@authenticate_user
async def protected_route(request: Request):
    user = request.state.user
    return {"message": f"Hello, {user['username']}. You have access to this protected route."}

# This is a public endpoint
@app.get("/public/")
async def public_route():
    return {"message": "Hello, this is a public route."}

# This is an example of a protected endpoint that needs authentication and authorization
@app.get("/admin/")
@authenticate_user
@authorize_roles("admin", "superadmin")
async def admin_route(request: Request):
    return {"message": "Hello, admin. You have access to this admin route."}