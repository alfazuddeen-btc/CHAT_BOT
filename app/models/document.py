from sqlalchemy import Column, Text, Integer
from app.core.database import Base
from pgvector.sqlalchemy import Vector

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=True)