# Authentification service
from fastapi import FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import jwt
from shared.auth import authenticate_user, authorize_roles, User, UserWithoutRole, TokenSchema

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


def create_jwt_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
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

# This is an example of a protected endpoint that needs authentication
@app.get("/test/auth/protected/")
@authenticate_user
async def protected_route(request: Request):
    user = request.state.user
    return {"message": f"Hello, {user['username']}. You have access to this protected route."}

# This is a public endpoint
@app.get("/test/auth/public/")
async def public_route():
    return {"message": "Hello, this is a public route."}

# This is an example of a protected endpoint that needs authentication and authorization
@app.get("/test/auth/admin/")
@authenticate_user
@authorize_roles("admin", "superadmin")
async def admin_route(request: Request):
    return {"message": "Hello, admin. You have access to this admin route."}