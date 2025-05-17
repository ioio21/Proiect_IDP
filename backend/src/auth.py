"""Authentication service for managing user login, registration, and access control.

This module provides functionality for user authentication and authorization,
including password hashing, JWT token generation, and role-based access control.
"""
import os
from datetime import datetime, timedelta

import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from .services.database import get_db
from .services import crud
from .shared.auth import authenticate_user, authorize_roles, UserWithoutRole, TokenSchema
from .shared.metrics import setup_metrics

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()
# Setup Prometheus metrics
setup_metrics(app)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt algorithm.

    Args:
        password: The plain text password to hash

    Returns:
        The hashed password string
    """
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against

    Returns:
        True if the password matches the hash, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

# Fake database. To be removed
fake_db = {
    "admin": {
        "password": hash_password("admin"),
        "role": "admin",
    }
}


def create_jwt_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT token with the provided data and expiration.

    Args:
        data: The payload data to encode in the token
        expires_delta: Optional time delta for token expiration

    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY.encode(), ALGORITHM)

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint to verify service status."""
    return {"status": "healthy"}

# User registration
@app.post("/register/")
async def register(user: UserWithoutRole, db = Depends(get_db)) -> dict:
    """Register a new user.

    Args:
        user: User object containing username and password

    Returns:
        A message confirming successful registration

    Raises:
        HTTPException: If the username is already registered
    """
    if user.username in fake_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    crud.create_user(db, user.username, user.password)
    return {"message": "User registered successfully"}

# User login
@app.post("/login/", response_model=TokenSchema)
async def login(user: UserWithoutRole, db = Depends(get_db)) -> dict:
    """Authenticate a user and generate a JWT token.

    Args:
        user: User object containing username and password

    Returns:
        A token object containing the JWT token and token type

    Raises:
        HTTPException: If the credentials are invalid
    """
    if crud.get_user_by_username(db, user.username) is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    role = crud.get_user_by_username(db, user.username).role
    token = create_jwt_token(
        {"sub": user.username, "role": role},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"token": token, "token_type": "bearer"}

# This is an example of a protected endpoint that needs authentication
@app.get("/test/auth/protected/")
@authenticate_user
async def protected_route(request: Request):
    """Protected route that requires authentication.

    Args:
        request: The request object containing user information

    Returns:
        A message confirming access to the protected route
    """
    user = request.state.user
    return {"message": f"Hello, {user['username']}. You have access to this protected route."}

# This is a public endpoint
@app.get("/test/auth/public/")
async def public_route():
    """Public route that doesn't require authentication.

    Returns:
        A message indicating this is a public route
    """
    return {"message": "Hello, this is a public route. v2"}

# This is an example of a protected endpoint that needs authentication and authorization
@app.get("/test/auth/admin/")
@authenticate_user
@authorize_roles("admin", "superadmin")
async def admin_route(_request: Request):
    """Admin route that requires authentication and admin role.

    Args:
        _request: The request object (unused but required by decorator)

    Returns:
        A message confirming access to the admin route
    """
    return {"message": "Hello, admin. You have access to this admin route."}