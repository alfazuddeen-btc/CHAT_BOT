from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime
import uuid

class UserBatch(Base):
    __tablename__ = "user_batches"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    recent_messages = Column(Text, nullable=False, default="[]")  # JSON
    batch_count = Column(Integer, default=0)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())