from langchain_community.vectorstores.pgvector import PGVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from app.core.database import SessionLocal
from app.models.document import Document as DBDocument
import os
from dotenv import load_dotenv

load_dotenv(override=True)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:123@localhost:5434/postgres"
)


def ingest_to_langchain():
    db = SessionLocal()

    print("=" * 60)
    print("INGESTING DOCUMENTS TO LANGCHAIN PGVECTOR")
    print("=" * 60)

    try:
        docs = db.query(DBDocument).all()
        print(f"\nFound {len(docs)} documents in database")

        if len(docs) == 0:
            print(" No documents in database! Run add_documents_simple.py first")
            return

        connection_string = DATABASE_URL.replace("+psycopg2", "")

        vector_store = PGVector(
            connection_string=connection_string,
            embedding_function=embeddings,
            collection_name="langchain"
        )

        langchain_docs = []
        for doc in docs:
            langchain_doc = Document(
                page_content=doc.content,
                metadata={"source": "medical_document", "topic": "medical"}
            )
            langchain_docs.append(langchain_doc)

        print(f"\nConverted {len(langchain_docs)} documents for LangChain")

        print("\nAdding documents to LangChain PGVector...")
        vector_store.add_documents(langchain_docs)

        print("=" * 60)
        print(f"SUCCESSFULLY INGESTED {len(langchain_docs)} DOCUMENTS!")
        print("=" * 60)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("This will ingest documents from database to LangChain PGVector")
    print("\nContinue? (yes/no): ", end="")

    if input().strip().lower() == "yes":
        ingest_to_langchain()
    else:
        print("Cancelled.")