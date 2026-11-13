
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


# Check that all required database settings are available
required_settings = [
    settings.DB_HOST,
    settings.DB_NAME,
    settings.DB_USER,
    settings.DB_PASSWORD,
    settings.DB_PORT,
]

if not all(required_settings):
    raise ValueError("Missing database configuration. Check your .env file.")


# Build the database connection URL safely
database_url = URL.create(
    drivername="mysql+pymysql",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=int(settings.DB_PORT),
    database=settings.DB_NAME,
)


# Create the database engine
engine = create_engine(
    database_url,
    pool_pre_ping=True,
)


# Create a reusable database session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


# Base class for all SQLAlchemy models
class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
