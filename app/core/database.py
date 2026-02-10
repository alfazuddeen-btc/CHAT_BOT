from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from app.core.config import settings
# from app.models.user_batch import UserBatch

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


