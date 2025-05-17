"""Database connection and session management module."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Încărcăm variabilele de mediu
load_dotenv()

DATABASE_URL = "postgresql://postgres:admin@localhost:5432/app"

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
