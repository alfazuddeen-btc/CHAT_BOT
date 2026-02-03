from datetime import datetime
from app.models.consent import Consent

def has_active_consent(db, user_id: str) -> bool:
    consent = db.query(Consent).filter(Consent.user_id == user_id).first()
    return bool(consent and consent.accepted)

def record_consent(db, user_id: str):
    consent = db.query(Consent).filter(Consent.user_id == user_id).first()

    if not consent:
        consent = Consent(
            user_id=user_id,
            accepted=True,
            accepted_at=datetime.utcnow()
        )
        db.add(consent)
    else:
        consent.accepted = True
        consent.accepted_at = datetime.utcnow()

    db.commit()
    print(f"Consent recorded for user: {user_id}")