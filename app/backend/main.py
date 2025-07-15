from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.routers.receipts import router
from routers import receipts
import os

app = FastAPI(
    title="Philippine Receipt OCR API",
    description="AI-powered receipt processing for Philippine businesses",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "Philippine Receipt OCR API",
        "status": "running",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "receipt-ocr-api"
    }