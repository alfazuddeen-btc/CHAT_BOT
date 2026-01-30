from app.rag.vector_store import VectorStore
from app.core.llm import get_llm_response
from app.logic.summary_manager import get_user_summary
from app.core.config import settings

vector_store = VectorStore()

def is_medical_query(query: str) -> bool:
    if not query or len(query.strip()) < 2:
        return True

    query_lower = query.lower().strip()
    if any(word in query_lower for word in
           ["document", "information", "tell me", "explain", "details", "about", "what is", "how"]):
        return True

    prompt = f"""Is this query medical-related? Answer with ONLY: YES or NO

Query: "{query}"

YES if: health, symptoms, diseases, medications, treatments, wellness, exercise, diet, medical advice, or asking for medical information
NO if: booking, shopping, entertainment, jobs, finance, anything non-medical

Answer only YES or NO."""

    try:
        response = get_llm_response(prompt).strip().upper()
        return "YES" in response
    except Exception as e:
        print(f"Error in medical query check: {e}")
        return True

def get_rag_response(db, user_id: str, query: str, history: list, language: str = "en") -> str:

    if not is_medical_query(query):
        if language == "hi":
            return """❌ मैं केवल चिकित्सा संबंधी प्रश्नों में मदद कर सकता हूं।

यदि आपके पास कोई चिकित्सा प्रश्न हैं, तो बेझिझक पूछें।"""
        else:
            return """❌ I can only help with medical-related questions.

If you have any medical questions, feel free to ask."""

    try:
        vector_store.set_db(db)
        retrieved_docs = vector_store.query(
            query_text=query,
            top_k=settings.TOP_K
        )

    except Exception as e:
        print(f"Error retrieving documents: {e}")
        retrieved_docs = []

    if not retrieved_docs:
        return "I don't have information about that medical topic. Please consult a healthcare professional."

    context = "\n".join(doc["content"] for doc in retrieved_docs)
    summary = get_user_summary(db, user_id)

    conversation = ""
    for msg in history:
        conversation += f"{msg['role'].upper()}: {msg['content']}\n"

    prompt = f"""You are a medical assistant. Answer this medical question based on the information provided.

Language: Respond in {language.upper()}

Medical Information:
{context}

User Summary:
{summary if summary else "No summary available."}

Previous Conversation:
{conversation if conversation else "No previous conversation."}

Question: {query}

Answer the question clearly and concisely. Respond in {language.upper()}. Do NOT mention documents or personal details."""

    try:
        response = get_llm_response(prompt)
        return response
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Unable to generate response. Please try again."