from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.database import engine
from app.routers import auth, events, users, discord

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Event Attendance API",
    description="API for tracking event attendance with Discord bot integration",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(events.router)
app.include_router(discord.router)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Event Attendance API with Discord Integration",
        "docs": "/docs",
        "version": "2.0.0",
        "features": [
            "Time-based attendance (only during events)",
            "Discord bot integration",
            "JWT authentication",
            "Event management"
        ]
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"} 