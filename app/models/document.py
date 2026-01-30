from sqlalchemy import Column, Integer, Text, JSON
from pgvector.sqlalchemy import Vector
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(dim=384), nullable=False)
    metadata_json = Column(JSON, nullable=True)

    doc_metadata = Column(JSON, nullable=True)
