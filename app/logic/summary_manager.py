from app.core.llm import get_llm_response

try:
    from app.logic.user_summary import UserSummary
except ImportError:
    from app.logic.user_summary import UserSummary

def update_user_summary(db, user_id: str, recent_messages: list):
    conversation = ""
    for msg in recent_messages:
        conversation += f"{msg['role']}: {msg['content']}\n"

    prompt = f"""
Summarize the following medical conversation concisely. Keep only medically relevant facts.

Conversation:
{conversation}

Return a short paragraph summary.
"""

    try:
        new_summary = get_llm_response(prompt)
    except Exception as e:
        print(f"Error generating summary: {e}")
        new_summary = "Summary generation in progress..."

    summary = db.query(UserSummary).filter_by(user_id=user_id).first()

    if summary:
        summary.summary = new_summary
    else:
        summary = UserSummary(user_id=user_id, summary=new_summary)
        db.add(summary)

    db.commit()
    print(f"Summary updated for user: {user_id}")

def get_user_summary(db, user_id: str) -> str:
    try:
        summary = db.query(UserSummary).filter_by(user_id=user_id).first()
        return summary.summary if summary else ""
    except Exception as e:
        print(f"Error fetching summary: {e}")
        return ""