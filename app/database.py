from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# For PostgreSQL, check if connection string needs tweaks (like removing schema)
db_url = settings.database_url
if "?schema=" in db_url:
    db_url = db_url.split("?schema=")[0]

try:
    # Test engine creation and connection
    if db_url.startswith("postgresql"):
        temp_engine = create_engine(db_url, connect_args={"connect_timeout": 2})
        with temp_engine.connect() as conn:
            pass
        engine = temp_engine
        print("Connected to PostgreSQL successfully.")
    else:
        engine = create_engine(db_url)
except Exception as e:
    print(f"PostgreSQL connection failed: {e}. Falling back to SQLite local database.")
    # Fallback to local SQLite database
    sqlite_url = "sqlite:///./astrolab.db"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
