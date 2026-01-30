from app.models.document import Document
from app.core.config import settings
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
import warnings
from sqlalchemy import text

warnings.filterwarnings("ignore")

class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.db = None

    def set_db(self, db: Session):

        self.db = db

    def add_document(self, content: str, metadata: dict = None):

        if not self.db:
            raise ValueError("Database session not set. Call set_db() first.")

        embedding = self.model.encode(content).tolist()
        doc = Document(
            content=content,
            embedding=embedding,
            metadata_json=metadata
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def query(self, query_text: str, top_k: int = None):

        if not self.db:
            raise ValueError("Database session not set. Call set_db() first.")

        if top_k is None:
            top_k = settings.TOP_K

        try:
            query_vector = self.model.encode(query_text).tolist()
            results = (
                self.db.query(Document)
                .order_by(Document.embedding.cosine_distance(query_vector))
                .limit(top_k)
                .all()
            )

            return [
                {"content": r.content, "metadata": r.metadata_json}
                for r in results
            ]
        except Exception as e:
            print(f"Error querying documents: {e}")
            return []

    def similarity_search(self, query_embedding, limit=3):

        if not self.db:
            raise ValueError("Database session not set. Call set_db() first.")

        try:
            sql = """
                  SELECT content, metadata_json
                  FROM documents
                  ORDER BY embedding <=> :query_embedding 
                LIMIT :limit \
                  """
            return self.db.execute(
                text(sql),
                {
                    "query_embedding": query_embedding,
                    "limit": limit
                }
            ).fetchall()
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []