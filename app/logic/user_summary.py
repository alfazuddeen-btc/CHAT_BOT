from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class UserSummary(Base):
    __tablename__ = "user_summaries"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    summary = Column(Text, nullable=False, default="")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())

    def __repr__(self):
        return f"<UserSummary(user_id={self.user_id}, updated_at={self.updated_at})>"