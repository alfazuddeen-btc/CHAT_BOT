from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime
from app.core.database import Base
import uuid

class Chat(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=False, index=True)

    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())

    def __repr__(self):
        return f"<Chat(id='{self.id}', user_id='{self.user_id}', session_id='{self.session_id}')>"