"""Database connection and session management module."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Încărcăm variabilele de mediu
load_dotenv()

# Get database configuration from environment variables
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "app")

# Construct the database URL without any protocol prefixes in the host
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

print(DATABASE_URL)

# Creare engine SQLAlchemy
engine = create_engine(DATABASE_URL)

# Creare sesiune
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Baza pentru modelele declarative
Base = declarative_base()

# Funcție de utilitate pentru a obține o sesiune DB
def get_db():
    """Return a database session that will be automatically closed when finished."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
