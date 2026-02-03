from langchain_community.vectorstores.pgvector import PGVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

from app.logic.summarization_memory import SummarizationMemory

load_dotenv(override=True)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:123@localhost:5434/postgres"
)


class LangChainRAG:
    def __init__(self, max_recent_messages: int = 10):
        self.embeddings = embeddings
        self.llm = llm
        self.vector_store = None
        self.max_recent_messages = max_recent_messages
        self.memory = None

        print(f"✅ LangChain RAG initialized")
        print(f"   Max recent messages: {max_recent_messages}")

        self._initialize_vector_store()

    def _initialize_vector_store(self):
        try:
            connection_string = DATABASE_URL.replace("+psycopg2", "")

            self.vector_store = PGVector(
                connection_string=connection_string,
                embedding_function=self.embeddings,
                collection_name="langchain"
            )
            print("✓ LangChain PGVector initialized")
        except Exception as e:
            print(f"✗ Error initializing vector store: {e}")
            raise

    def create_memory(self, db, user_id: str) -> SummarizationMemory:
        memory = SummarizationMemory(
            db=db,
            user_id=user_id,
            max_recent=self.max_recent_messages
        )

        return memory

    def query(self, question: str, memory: SummarizationMemory,
              language: str = "en") -> dict:

        try:
            print(f"\n{'=' * 60}")
            print(f"RAG QUERY WITH SUMMARIZATION MEMORY")
            print(f"{'=' * 60}")
            print(f"Question: {question}")

            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )
            retrieved_docs = retriever.invoke(question)

            print(f"\nRetrieved {len(retrieved_docs)} documents")

            if len(retrieved_docs) == 0:
                return {
                    "answer": "I don't have information about that topic.",
                    "sources": [],
                    "memory_stats": memory.get_stats(),
                    "success": True
                }
            memory_context = memory.get_memory_context()

            print(f"\n Memory:")
            stats = memory.get_stats()
            print(f"   Summary: {stats['summary_length']} chars")
            print(f"   Recent messages: {stats['recent_messages']}")
            print(f"   Total context: {stats['total_characters']} chars")

            context_docs = "\n\n".join([
                f"[{doc.metadata.get('source', 'Source')}]\n{doc.page_content}"
                for doc in retrieved_docs
            ])

            if language == "hi":
                prompt_template = """आप एक चिकित्सा सहायक हैं।

पिछली बातचीत:
{memory}

चिकित्सा संदर्भ:
{context}

प्रश्न: {question}

उत्तर:"""
            else:
                prompt_template = """You are a helpful medical assistant.

Previous conversation:
{memory}

Medical context:
{context}

Question: {question}

Answer:"""

            prompt = prompt_template.format(
                memory=memory_context if memory_context else "No previous conversation",
                context=context_docs,
                question=question
            )

            print(f"\n Calling LLM...")

            response = self.llm.invoke(prompt)
            answer = response.content

            print(f" LLM Response received")

            print(f"\n Updating memory...")
            memory.add_message(question, answer)

            memory.save_to_database()

            print(f"\n{'=' * 60}")
            print(f"QUERY COMPLETE")
            print(f"{'=' * 60}\n")

            return {
                "answer": answer,
                "sources": [
                    {
                        "source": doc.metadata.get("source", "Unknown"),
                        "topic": doc.metadata.get("topic", "general")
                    }
                    for doc in retrieved_docs
                ],
                "memory_stats": memory.get_stats(),
                "success": True
            }

        except Exception as e:
            print(f" Error in RAG query: {e}")
            import traceback
            traceback.print_exc()
            return {
                "answer": "I encountered an error.",
                "sources": [],
                "memory_stats": memory.get_stats() if memory else {},
                "success": False,
                "error": str(e)
            }

_rag_instance = None


def get_rag_pipeline(max_recent_messages: int = 10):

    global _rag_instance
    if _rag_instance is None:
        try:
            _rag_instance = LangChainRAG(max_recent_messages=max_recent_messages)
        except Exception as e:
            print(f"✗ Failed to initialize RAG: {e}")
            return None
    return _rag_instance


def get_rag_response(db, user_id: str, query: str, history: list,
                     language: str = "en") -> str:
    try:
        rag = get_rag_pipeline(max_recent_messages=10)
        if rag is None:
            return "RAG system is not initialized."

        memory = rag.create_memory(db, user_id)

        memory.load_from_database(history)

        result = rag.query(query, memory, language)

        if result["success"]:
            stats = result['memory_stats']
            print(f"\n Memory Stats:")
            print(f"   Summary length: {stats['summary_length']} chars")
            print(f"   Recent messages: {stats['recent_messages']}")
            print(f"   Total context: {stats['total_characters']} chars")

            return result["answer"]
        else:
            return "I encountered an error. Please try again."

    except Exception as e:
        print(f" Error in get_rag_response: {e}")
        import traceback
        traceback.print_exc()
        return "Unable to process your query."