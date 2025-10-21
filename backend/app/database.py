from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Отримуємо DATABASE_URL з environment
DATABASE_URL = os.getenv("DATABASE_URL")

# ВАЖЛИВО: Railway PostgreSQL вимагає postgresql+psycopg2://
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Додаємо параметри з'єднання для стабільності
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Перевіряє з'єднання перед використанням
    pool_recycle=300,    # Перевикористовує з'єднання кожні 5 хвилин
    echo=False           # Не логує SQL запити (можна True для debug)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency для FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()