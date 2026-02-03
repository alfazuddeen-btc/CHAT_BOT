from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.chat import Chat
from datetime import datetime, timedelta
import hashlib
import uuid

from app.core.jwt_auth import create_access_token, verify_token

router = APIRouter()
security = HTTPBearer()

class LoginRequest(BaseModel):
    name: str
    dob: str
    pin: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    name: str
    message: str


class ChatRequest(BaseModel):
    message: str
    session_id: str
    language: str = "en"


class ChatResponse(BaseModel):
    response: str
    session_id: str


TRANSLATIONS = {
    "en": {
        "welcome": """👋 **Welcome to Medical Assistant**

I'm your intelligent medical assistant powered by AI. I can help you with:

✅ Medical questions and information
✅ Health advice and guidance
✅ Disease information and symptoms
✅ Wellness tips

⚠️ **Important:** I provide general medical information, not professional diagnosis. Always consult a doctor for serious concerns.

Before we proceed, I need your consent to store our conversation data.""",

        "consent_prompt": """📋 **Consent Required**

To continue, please provide your consent:

Your data will be:
- Stored securely in our encrypted database
- Used only for medical assistance
- Never shared with third parties

Type: **"I agree"** or **"I consent"**""",

        "consent_confirmed": """✅ **Consent Confirmed**

Thank you! You can now ask me medical questions.""",

        "clarification": """❓ **I need clarification**

{question}

Are you asking about:
1. Medical/health topic
2. Information about me
3. Something else""",

        "general_response_intro": "Great question! ",

        "not_medical": """❌ I can only help with medical-related questions.

Please ask me about:
- Symptoms and conditions
- Health information
- Medical treatments
- Wellness advice""",
    },

    "hi": {
        "welcome": """👋 **चिकित्सा सहायक में आपका स्वागत है**

मैं आपका AI-संचालित चिकित्सा सहायक हूं। मैं आपकी मदद कर सकता हूं:

✅ चिकित्सा प्रश्न और जानकारी
✅ स्वास्थ्य सलाह
✅ रोग की जानकारी
✅ स्वास्थ्य सुझाव

⚠️ **महत्वपूर्ण:** मैं सामान्य चिकित्सा जानकारी देता हूं, निदान नहीं। गंभीर समस्याओं के लिए हमेशा डॉक्टर से मिलें।

शुरू करने से पहले, कृपया अपनी सहमति दें।""",

        "consent_prompt": """📋 **सहमति आवश्यक**

जारी रखने के लिए, कृपया सहमति दें:

आपका डेटा:
- हमारे एन्क्रिप्टेड डेटाबेस में सुरक्षित रूप से संग्रहीत
- केवल चिकित्सा सहायता के लिए उपयोग
- किसी से साझा नहीं किया जाएगा

टाइप करें: **"सहमत हूं"** या **"मैं सहमत हूं"**""",

        "consent_confirmed": """✅ **सहमति की पुष्टि**

धन्यवाद! अब आप मुझसे चिकित्सा प्रश्न पूछ सकते हैं।""",

        "clarification": """❓ **स्पष्टीकरण की आवश्यकता**

{question}

क्या आप पूछ रहे हैं:
1. चिकित्सा/स्वास्थ्य विषय
2. मेरे बारे में जानकारी
3. कुछ और""",

        "general_response_intro": "शानदार सवाल! ",

        "not_medical": """❌ मैं केवल चिकित्सा-संबंधित प्रश्नों में मदद कर सकता हूं।

मुझसे पूछें:
- लक्षण और स्थितियां
- स्वास्थ्य जानकारी
- चिकित्सा उपचार
- स्वास्थ्य सलाह""",
    }
}


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    token = credentials.credentials
    return verify_token(token)


def save_chat_message(db: Session, user_id: str, session_id: str, message: str, response: str):
    try:
        chat = Chat(
            user_id=user_id,
            session_id=session_id,
            message=message,
            response=response,
            timestamp=datetime.utcnow()
        )
        db.add(chat)
        db.commit()
        print(f"Saved chat message for user {user_id}")
    except Exception as e:
        print(f" Error saving chat: {e}")
        db.rollback()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        print("=" * 60)
        print("LOGIN REQUEST RECEIVED (JWT)")
        print("=" * 60)

        if not request.name or not request.name.strip():
            raise HTTPException(status_code=400, detail="Name is required")

        if not request.dob:
            raise HTTPException(status_code=400, detail="Date of birth is required")

        if not request.pin or len(request.pin) != 4:
            raise HTTPException(status_code=400, detail="Valid 4-digit PIN is required")

        pin_hash = hashlib.sha256(request.pin.encode()).hexdigest()

        user = db.query(User).filter(
            User.name == request.name,
            User.dob == request.dob
        ).first()

        if user:
            if user.is_locked:
                raise HTTPException(
                    status_code=403,
                    detail="Account locked. Contact support."
                )
            if user.pin_hash != pin_hash:
                print(f" Invalid PIN for user: {request.name}")
                user.failed_attempts += 1
                if user.failed_attempts >= 3:
                    user.is_locked = True
                    db.commit()
                    raise HTTPException(status_code=401, detail="Account locked.")
                db.commit()
                raise HTTPException(status_code=401, detail=f"Invalid PIN. {3 - user.failed_attempts} attempts left.")

            user.failed_attempts = 0
            db.commit()
            print(f" User authenticated: {request.name} with ID: {user.user_id}")

        else:
            user_id = hashlib.sha256(f"{request.name}{request.dob}{request.pin}".encode()).hexdigest()[:16]
            user = User(
                user_id=user_id,
                name=request.name,
                dob=request.dob,
                pin_hash=pin_hash,
                failed_attempts=0,
                is_locked=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created new user: {request.name} with ID: {user_id}")

        access_token = create_access_token(
            data={
                "sub": user.user_id,
                "name": user.name
            }
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.user_id,
            name=user.name,
            message="Login successful! Secured with JWT"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in login: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat(
        request: ChatRequest,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    try:
        print("=" * 60)
        print("CHAT REQUEST RECEIVED (JWT + LangChain Memory)")
        print("=" * 60)
        print(f"User ID: {current_user['sub']}")
        print(f"User Name: {current_user['name']}")
        print(f"Message: {request.message}")
        print(f"Language: {request.language}")
        print("=" * 60)

        user_id = current_user["sub"]
        language = request.language if request.language in TRANSLATIONS else "en"
        t = TRANSLATIONS[language]

        total_messages = db.query(Chat).filter(Chat.user_id == user_id).count()
        print(f" Total messages so far: {total_messages}")

        if total_messages == 0:
            message_lower = request.message.lower().strip()
            consent_keywords = ["agree", "consent", "accept", "yes", "ok", "सहमत", "सहमति", "स्वीकार", "हाँ", "हां"]
            has_consent = any(keyword in message_lower for keyword in consent_keywords)

            if not has_consent:
                response = t["consent_prompt"]
                save_chat_message(db, user_id, request.session_id, request.message, response)
                return ChatResponse(response=response, session_id=request.session_id)
            else:
                from app.logic.consent_manager import record_consent
                record_consent(db, user_id)
                response = t["consent_confirmed"]
                save_chat_message(db, user_id, request.session_id, request.message, response)
                return ChatResponse(response=response, session_id=request.session_id)

        print(f"Message #{total_messages + 1} - classifying intent")

        from app.logic.intent_classifier_advanced import classify_intent, get_clarification_question
        from app.logic.chat_history_loader import load_chat_history

        history = load_chat_history(db, user_id)

        intent = classify_intent(request.message)
        print(f" Intent: {intent}")

        if intent == "MEDICAL":
            print(f" MEDICAL: Using LangChain RAG with Summarization Memory")

            from app.rag.langchain_rag_FINAL import get_rag_response

            bot_response = get_rag_response(db, user_id, request.message, history, language)

        elif intent == "GENERAL_CHAT":
            print(f" GENERAL_CHAT: Friendly response with memory")
            from app.core.llm import get_llm_response
            from app.rag.langchain_rag_FINAL import get_rag_pipeline

            rag = get_rag_pipeline(max_recent_messages=10)
            memory = rag.create_memory(db, user_id)
            memory.load_from_database(history)

            memory_context = memory.get_memory_context()

            if language == "hi":
                prompt = f"""आप एक चिकित्सा सहायक हैं।

पिछली बातचीत:
{memory_context if memory_context else "कोई पिछली बातचीत नहीं"}

प्रश्न: {request.message}

मैत्रीपूर्ण तरीके से जवाब दें। कृपया पिछली बातचीत का संदर्भ दें यदि प्रासंगिक हो।"""
            else:
                prompt = f"""You are a helpful medical assistant.

Previous conversation:
{memory_context if memory_context else "No previous conversation"}

Question: {request.message}

Respond in a friendly way. If they ask about previous conversations, 
refer to the context above. Keep response short (2-3 sentences).
Always remind them you provide information, not diagnosis."""

            bot_response = get_llm_response(prompt)

            memory.add_message(request.message, bot_response)
            memory.save_to_database()

        elif intent == "AMBIGUOUS":
            print(f" AMBIGUOUS: Asking clarification")
            from app.rag.langchain_rag_FINAL import get_rag_pipeline

            rag = get_rag_pipeline(max_recent_messages=10)
            memory = rag.create_memory(db, user_id)
            memory.load_from_database(history)

            clarification = get_clarification_question(request.message)
            bot_response = t["clarification"].format(question=clarification)

            memory.add_message(request.message, bot_response)
            memory.save_to_database()

        else:
            print(f" OTHER: Non-medical query")
            from app.rag.langchain_rag_FINAL import get_rag_pipeline

            rag = get_rag_pipeline(max_recent_messages=10)
            memory = rag.create_memory(db, user_id)
            memory.load_from_database(history)

            bot_response = t["not_medical"]

            memory.add_message(request.message, bot_response)
            memory.save_to_database()

        save_chat_message(db, user_id, request.session_id, request.message, bot_response)

        message_count = db.query(Chat).filter(Chat.user_id == user_id).count()
        if message_count % 5 == 0:
            try:
                print(f"Updating user summary (message #{message_count})...")
                from app.logic.summary_manager import update_user_summary
                recent_history = load_chat_history(db, user_id)
                update_user_summary(db, user_id, recent_history)
                print(f"Summary updated")
            except Exception as e:
                print(f" Failed to update summary: {e}")
        return ChatResponse(response=bot_response, session_id=request.session_id)

    except HTTPException:
        raise
    except Exception as e:
        print(f" Error in chat: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/history/user/{user_id}")
async def get_user_chat_history(
        user_id: str,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):

    if current_user["sub"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        chats = db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.timestamp).all()
        return {
            "user_id": user_id,
            "total_messages": len(chats),
            "messages": [
                {
                    "message": chat.message,
                    "response": chat.response,
                    "timestamp": chat.timestamp.isoformat(),
                    "session_id": chat.session_id
                }
                for chat in chats
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/history/{session_id}")
async def get_chat_history(
        session_id: str,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    try:
        chats = db.query(Chat).filter(Chat.session_id == session_id).order_by(Chat.timestamp).all()
        if chats and chats[0].user_id != current_user["sub"]:
            raise HTTPException(status_code=403, detail="Access denied")

        return {
            "session_id": session_id,
            "messages": [
                {
                    "message": chat.message,
                    "response": chat.response,
                    "timestamp": chat.timestamp.isoformat()
                }
                for chat in chats
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/summary")
async def get_user_summary(
        user_id: str,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["sub"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        from app.logic.summary_manager import get_user_summary as fetch_summary
        summary = fetch_summary(db, user_id)
        return {
            "user_id": user_id,
            "summary": summary or "No summary yet.",
            "has_summary": bool(summary)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/initial-message/{user_id}")
async def get_initial_message(
        user_id: str,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["sub"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        total_messages = db.query(Chat).filter(Chat.user_id == user_id).count()
        from app.logic.consent_manager import has_active_consent
        has_consent = has_active_consent(db, user_id)

        if total_messages == 0:
            return {
                "message": TRANSLATIONS["en"]["welcome"] + "\n\n" + TRANSLATIONS["en"]["consent_prompt"],
                "is_new_user": True
            }
        elif has_consent:
            return {
                "message": None,
                "is_new_user": False
            }
        else:
            return {
                "message": TRANSLATIONS["en"]["consent_prompt"],
                "is_new_user": False
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))