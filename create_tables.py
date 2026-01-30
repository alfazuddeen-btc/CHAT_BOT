from app.core.database import engine, Base
from app.models.user import User
from app.models.chat import Chat
from app.models.document import Document
from app.models.consent import Consent

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("All tables created successfully.")
