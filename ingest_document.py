from app.core.database import get_db
from app.rag.vector_store import VectorStore
from app.rag.document_loader import load_documents_from_txt

def main():
    db = next(get_db())
    vector_store = VectorStore()
    vector_store.set_db(db)

    load_documents_from_txt("data", vector_store)

if __name__ == "__main__":
    main()
