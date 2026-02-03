from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.api import chat_routes, user_routes
import os

# Import models to ensure they're registered
from app.models.user import User
from app.models.chat import Chat
from app.models.consent import Consent
from app.models.document import Document

try:
    from app.logic import user_summary as user_summary_module

    if hasattr(user_summary_module, 'UserSummary'):
        UserSummary = user_summary_module.UserSummary
except Exception as e:
    print(f"Warning: Could not import UserSummary: {e}")
    UserSummary = None

app = FastAPI(
    title="Medical RAG Assistant",
    description="A RAG-based medical assistant with user authentication",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    try:
        Base.metadata.create_all(bind=engine)

        print("=" * 60)
        print(" DATABASE INITIALIZED SUCCESSFULLY!")
        print("=" * 60)
        print("Tables created:")
        print("  • users")
        print("  • chat_messages")
        print("  • consents")
        print("  • user_summaries")
        print("  • documents")
        print("=" * 60)
        print("Medical RAG Assistant is ready!")
        print("=" * 60)

    except Exception as e:
        print("=" * 60)
        print(" ERROR DURING STARTUP")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)

@app.on_event("shutdown")
def shutdown_event():
    print("=" * 60)
    print(" Medical RAG Assistant shutting down...")
    print("=" * 60)

app.include_router(chat_routes.router, tags=["chat"])
app.include_router(user_routes.router, tags=["health"])

@app.get("/")
def read_root():
    return {
        "message": "Medical RAG Assistant API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "login": "/login",
            "chat": "/chat"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Medical RAG Assistant",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )