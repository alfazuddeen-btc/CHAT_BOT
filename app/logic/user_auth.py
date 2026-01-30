from sqlalchemy.orm import Session
from app.models.user import User
from datetime import date
from app.core.security import hash_pin, verify_pin, validate_pin_format

def create_user(db: Session, name: str, dob: date, pin: str):
    if not validate_pin_format(pin):
        return None, "INVALID_PIN_FORMAT"

    hashed_pin = hash_pin(pin)
    new_user = User(
        name=name,
        dob=dob,
        pin_hash=hashed_pin,
        failed_attempts=0
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user, "USER_CREATED"

def identify_or_create_user(db: Session,name: str,dob: date,pin: str):
    existing_user = (
        db.query(User)
        .filter(User.name == name, User.dob == dob)
        .first()
    )
    if existing_user:
        if existing_user.failed_attempts >= 5:
            return None, "USER_BLOCKED"

        if not verify_pin(pin, existing_user.pin_hash):
            existing_user.failed_attempts += 1
            db.commit()
            return None, "INVALID_PIN"

        existing_user.failed_attempts = 0
        db.commit()
        return existing_user, "AUTHENTICATED"

    else:
        return create_user(db, name, dob, pin)







