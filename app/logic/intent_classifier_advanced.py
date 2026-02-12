from app.core.llm import get_llm_response

def classify_intent(query: str) -> str:
    if not query or len(query.strip()) < 2:
        return "GREETING"

    prompt = f"""You are an intent classifier for a medical chatbot.

Classify the following user message into ONE category:

MEDICAL: Questions about health, symptoms, diseases, treatments, medications, medical conditions ,hospital
GENERAL_CHAT: Friendly casual conversation related to health/wellness (e.g., "how are you", "tell me about yourself")
AMBIGUOUS: Message is unclear or could be medical but not clear enough - need clarification
OTHER: Anything else (booking, shopping, entertainment, jobs, etc.)

User Message: "{query}"

Respond with ONLY the category name. Examples:
- "What is diabetes?" → MEDICAL
- "Hi, how are you?" → GENERAL_CHAT
- "Tell me something" → AMBIGUOUS
- "Book me a taxi" → OTHER
- "I have a headache" → MEDICAL
- "What can you do?" → GENERAL_CHAT

Category:"""

    try:
        response = get_llm_response(prompt).strip().upper()
        if "MEDICAL" in response:
            return "MEDICAL"
        elif "GENERAL_CHAT" in response:
            return "GENERAL_CHAT"
        elif "AMBIGUOUS" in response:
            return "AMBIGUOUS"
        elif "OTHER" in response:
            return "OTHER"
        else:
            return "GENERAL_CHAT"

    except Exception as e:
        print(f"Error classifying intent: {e}")
        return "GENERAL_CHAT"


def get_clarification_question(query: str) -> str:
    prompt = f"""User said: "{query}"

Generate ONE short clarification question to understand if they're asking about:
1. Medical/health topic
2. General information about you
3. Something else

Question should be natural and helpful. Keep it under 15 words."""

    try:
        return get_llm_response(prompt).strip()
    except:
        return "Could you clarify what you're asking about?"

