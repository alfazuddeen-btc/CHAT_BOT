from langchain_community.vectorstores import PGVector
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings


class LangChainRAG:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.vector_store = PGVector(
            connection_string=settings.DATABASE_URL,
            collection_name="langchain",
            embedding_function=self.embeddings,
        )


def get_rag_pipeline() -> LangChainRAG:
    return LangChainRAG()
