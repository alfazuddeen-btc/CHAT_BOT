from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'])

def hash_pin(pin: str):
    pin = pin.strip()
    pin = pin[:72]
    return pwd_context.hash(pin)

def verify_pin(pin: str, hashed: str) -> bool:
    pin = pin.strip()
    pin = pin[:72]
    return pwd_context.verify(pin, hashed)

def validate_pin_format(pin: str)->bool:
    return len(pin) == 4 and pin.isdigit()