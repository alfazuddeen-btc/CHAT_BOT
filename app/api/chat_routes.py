from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.chat import Chat
from datetime import datetime
import hashlib

router = APIRouter()

class LoginRequest(BaseModel):
    name: str
    dob: str
    pin: str

class LoginResponse(BaseModel):
    user_id: str
    name: str
    message: str

class ChatRequest(BaseModel):
    name: str
    dob: str
    pin: str
    session_id: str
    message: str
    language: str = "en"  # NEW: language parameter

class ChatResponse(BaseModel):
    response: str
    session_id: str

TRANSLATIONS = {
    "en": {
        "consent_required": """⚠️ Consent Required

Before we can discuss your medical concerns, we need your consent to store your conversation data in our database.

Your data will be:
• Stored securely in our encrypted database
• Used only to provide you with medical information
• Never shared with third parties

To provide consent, type: "I agree" or "I consent" """,

        "consent_needed": """❌ We need your consent to proceed.

Please type: "I agree" or "I consent" """,

        "consent_recorded": """✅ Thank you! Consent recorded. Your medical conversation data will be stored securely.

You can now ask me medical-related questions. If you have non-medical questions, I'll let you know I can only help with medical topics.""",
    },

    "hi": {
        "consent_required": """⚠️ सहमति आवश्यक

हम आपके चिकित्सा संबंधी मुद्दों पर चर्चा करने से पहले, आपको अपने बातचीत के डेटा को हमारे डेटाबेस में संग्रहीत करने की सहमति देनी होगी।

आपका डेटा:
• हमारे एन्क्रिप्टेड डेटाबेस में सुरक्षित रूप से संग्रहीत किया जाएगा
• केवल आपको चिकित्सा जानकारी प्रदान करने के लिए उपयोग किया जाएगा
• तीसरे पक्ष के साथ साझा नहीं किया जाएगा

सहमति देने के लिए टाइप करें: "सहमत हूं" या "मैं सहमत हूं" """,

        "consent_needed": """❌ हमें आपकी सहमति की आवश्यकता है।

कृपया टाइप करें: "सहमत हूं" या "मैं सहमत हूं" """,

        "consent_recorded": """✅ धन्यवाद! आपकी सहमति दर्ज की गई है। आपके चिकित्सा बातचीत का डेटा सुरक्षित रूप से संग्रहीत किया जाएगा।

अब आप मुझसे चिकित्सा संबंधी प्रश्न पूछ सकते हैं।""",
    }
}


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        print("=" * 60)
        print("LOGIN REQUEST RECEIVED")
        print("=" * 60)
        print(f"Name: {request.name}")
        print(f"DOB: {request.dob}")
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
                    detail="Account locked due to too many failed attempts. Please contact support."
                )
            if user.pin_hash != pin_hash:
                print(f"Invalid PIN for user: {request.name}")
                user.failed_attempts += 1

                if user.failed_attempts >= 3:
                    user.is_locked = True
                    db.commit()
                    raise HTTPException(
                        status_code=401,
                        detail="Account locked due to too many failed attempts."
                    )

                db.commit()
                raise HTTPException(
                    status_code=401,
                    detail=f"Invalid PIN. {3 - user.failed_attempts} attempts remaining."
                )

            user.failed_attempts = 0
            db.commit()
            print(f"User authenticated: {request.name} with ID: {user.user_id}")

            return LoginResponse(
                user_id=user.user_id,
                name=user.name,
                message="Login successful! Welcome back."
            )

        else:
            user_id = hashlib.sha256(f"{request.name}{request.dob}{request.pin}".encode()).hexdigest()[:16]

            new_user = User(
                user_id=user_id,
                name=request.name,
                dob=request.dob,
                pin_hash=pin_hash,
                failed_attempts=0,
                is_locked=False
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            print(f" Created new user: {request.name} with ID: {user_id}")

            return LoginResponse(
                user_id=new_user.user_id,
                name=new_user.name,
                message="Account created successfully! Welcome."
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f" Error in login endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


def get_or_create_user(db: Session, name: str, dob: str, pin: str):
    pin_hash = hashlib.sha256(pin.encode()).hexdigest()
    user = db.query(User).filter(
        User.name == name,
        User.dob == dob,
        User.pin_hash == pin_hash
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    return user


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
        print(f" Saved chat message for user {user_id}")
    except Exception as e:
        print(f" Error saving chat: {e}")
        db.rollback()


def generate_rag_response(user_id: str, message: str, db: Session, language: str = "en") -> str:
    from app.rag.rag_pipeline import get_rag_response
    from app.logic.chat_history_loader import load_chat_history

    try:
        history = load_chat_history(db, user_id)
        response = get_rag_response(
            db=db,
            user_id=user_id,
            query=message,
            history=history,
            language=language
        )

        return response

    except Exception as e:
        print(f"Error generating RAG response: {e}")
        import traceback
        traceback.print_exc()
        return "I'm unable to generate a response at the moment. Please try again."


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        print("=" * 60)
        print("CHAT REQUEST RECEIVED")
        print("=" * 60)
        print(f"Name: {request.name}")
        print(f"DOB: {request.dob}")
        print(f"Session ID: {request.session_id}")
        print(f"Message: {request.message}")
        print(f"Language: {request.language}")
        print("=" * 60)

        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        language = request.language if request.language in TRANSLATIONS else "en"

        user = get_or_create_user(db, request.name, request.dob, request.pin)

        # Count total messages BEFORE adding this message
        total_messages = db.query(Chat).filter(Chat.user_id == user.user_id).count()

        # FIRST MESSAGE ONLY - ask for consent
        if total_messages == 0:
            print(f"First message from user {user.user_id} - asking for consent")

            response = TRANSLATIONS[language]["consent_required"]

            save_chat_message(db, user.user_id, request.session_id, request.message, response)

            return ChatResponse(
                response=response,
                session_id=request.session_id
            )
        if total_messages == 1:
            message_lower = request.message.lower().strip()
            consent_keywords = [
                "agree", "consent", "accept", "yes", "ok", "okay", "sure", "yep", "yeah",
                "सहमत", "सहमति", "स्वीकार", "हाँ", "हां", "ठीक", "बिल्कुल"
            ]

            has_consent = any(keyword in message_lower for keyword in consent_keywords)

            if not has_consent:
                response = TRANSLATIONS[language]["consent_needed"]
                save_chat_message(db, user.user_id, request.session_id, request.message, response)
                return ChatResponse(
                    response=response,
                    session_id=request.session_id
                )
            else:
                from app.logic.consent_manager import record_consent
                record_consent(db, user.user_id)

                response = TRANSLATIONS[language]["consent_recorded"]

                save_chat_message(db, user.user_id, request.session_id, request.message, response)
                return ChatResponse(
                    response=response,
                    session_id=request.session_id
                )
        print(f"Message #{total_messages + 1} from user {user.user_id}")

        bot_response = generate_rag_response(user.user_id, request.message, db, language)

        save_chat_message(
            db=db,
            user_id=user.user_id,
            session_id=request.session_id,
            message=request.message,
            response=bot_response
        )
        message_count = db.query(Chat).filter(Chat.user_id == user.user_id).count()

        if message_count % 5 == 0:
            try:
                print(f"Updating user summary (message #{message_count})...")
                from app.logic.summary_manager import update_user_summary
                from app.logic.chat_history_loader import load_chat_history

                recent_history = load_chat_history(db, user.user_id)
                update_user_summary(db, user.user_id, recent_history)
                print(f"Summary updated for user {user.user_id}")
            except Exception as e:
                print(f" Failed to update summary: {e}")

        return ChatResponse(
            response=bot_response,
            session_id=request.session_id
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    try:
        chats = db.query(Chat).filter(
            Chat.session_id == session_id
        ).order_by(Chat.timestamp).all()

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
        print(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/history/user/{user_id}")
async def get_user_chat_history(user_id: str, db: Session = Depends(get_db)):
    try:
        chats = db.query(Chat).filter(
            Chat.user_id == user_id
        ).order_by(Chat.timestamp).all()

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
        print(f"Error fetching user history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/summary")
async def get_user_summary(user_id: str, db: Session = Depends(get_db)):
    try:
        from app.logic.summary_manager import get_user_summary as fetch_summary

        summary = fetch_summary(db, user_id)

        if not summary:
            return {
                "user_id": user_id,
                "summary": "No summary available yet. Summary will be generated after more conversations.",
                "has_summary": False
            }

        return {
            "user_id": user_id,
            "summary": summary,
            "has_summary": True
        }
    except Exception as e:
        print(f"Error fetching summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))