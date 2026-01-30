from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    dob = Column(String, nullable=False)
    pin_hash = Column(String, nullable=False)

    failed_attempts = Column(Integer, default=0, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_active_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(user_id='{self.user_id}', name='{self.name}')>"