from app.core.llm import get_llm_response

def is_medical_query(query: str) -> bool:
    if not query or len(query.strip()) < 2:
        return False

    prompt = f"""You are a medical query classifier. Classify if the following user query is medical-related.

User Query: "{query}"

Respond with ONLY one word:
- MEDICAL if the query is about health, medical conditions, symptoms, treatments, medications, diseases, wellness, nutrition, exercise, or any health-related topic
- NON_MEDICAL if the query is about booking, ordering, shopping, entertainment, jobs, finance, or anything NOT related to health/medical topics

Your response must be exactly: MEDICAL or NON_MEDICAL

Do not explain, just respond with one word."""

    try:
        response = get_llm_response(prompt).strip().upper()

        if "MEDICAL" in response and "NON_MEDICAL" not in response:
            return True
        elif "NON_MEDICAL" in response:
            return False
        else:
            return True

    except Exception as e:
        print(f"Error in medical query classification: {e}")
        return True


def classify_intent(message: str) -> str:

    if not message:
        return "general"

    message_lower = message.lower().strip()
    consent_keywords = [
        "agree", "consent", "accept", "yes", "okay", "sure",
        "yep", "yeah", "yup", "aye", "alright", "absolutely",
        "i agree", "i consent", "i accept",
        "go ahead", "proceed", "continue",
        "haan", "theek hai", "bilkul", "ji haan",
        "👍", "✓", "✔"
    ]

    for keyword in consent_keywords:
        if keyword in message_lower:
            return "consent"
    emergency_keywords = [
        "emergency", "urgent", "immediately", "right now", "help me",
        "can't breathe", "cant breathe", "chest pain", "heart attack",
        "stroke", "bleeding", "unconscious", "passed out", "dying",
        "severe pain", "911", "ambulance", "collapsed", "critical"
    ]

    if any(keyword in message_lower for keyword in emergency_keywords):
        return "emergency"
    diagnosis_keywords = [
        "do i have", "am i having", "is this", "diagnose me",
        "what's wrong with me", "whats wrong with me",
        "what disease", "which disease", "is it serious",
        "should i be worried", "do you think i have"
    ]

    if any(keyword in message_lower for keyword in diagnosis_keywords):
        return "diagnosis_request"
    return "general"

def is_consent_message(message: str) -> bool:
    return classify_intent(message) == "consent"

def is_emergency_message(message: str) -> bool:
    return classify_intent(message) == "emergency"