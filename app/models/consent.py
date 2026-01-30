from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime
from app.core.database import Base

class Consent(Base):
    __tablename__ = "consents"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    accepted = Column(Boolean, default=False)
    accepted_at = Column(DateTime, default=None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())

    def __repr__(self):
        return f"<Consent(user_id='{self.user_id}', accepted={self.accepted})>"