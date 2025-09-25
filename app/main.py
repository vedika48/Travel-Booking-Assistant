from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.api import travel, chat, services

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Travel Assistant API...")
    yield
    # Shutdown
    print("Shutting down Travel Assistant API...")

app = FastAPI(
    title="Travel Assistant API",
    description="Backend API for Travel Assistant Flutter App",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(travel.router, prefix="/api/travel", tags=["Travel Planning"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(services.router, prefix="/api/services", tags=["Services"])

@app.get("/")
async def root():
    return {"message": "Travel Assistant API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "travel-assistant-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)