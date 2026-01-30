from sqlalchemy.orm import Session
from app.models.chat import Chat

MAX_HISTORY = 10

def load_chat_history(db: Session, user_id: str):
    chats = (
        db.query(Chat)
        .filter(Chat.user_id == user_id)
        .order_by(Chat.timestamp.desc())
        .limit(MAX_HISTORY)
        .all()
    )
    chats.reverse()
    history = []
    for chat in chats:
        history.append({"role": "user", "content": chat.message})
        history.append({"role": "assistant", "content": chat.response})

    return history