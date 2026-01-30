import os
from app.rag.vector_store import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

vector_store = VectorStore()

def chunk_text(
    text: str,
    chunk_size: int = 400,
    chunk_overlap: int = 50
):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)

def load_documents_from_txt(folder_path: str, vector_store: VectorStore):
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            chunks = chunk_text(content)

            for i, chunk in enumerate(chunks):
                metadata = {
                    "source": filename,
                    "chunk_id": i
                }
                vector_store.add_document(chunk, metadata)

            print(f" Ingested {filename} with {len(chunks)} chunks")
