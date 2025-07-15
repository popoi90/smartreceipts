from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Philippine Receipt OCR API",
    description="AI-powered receipt processing for Philippine businesses",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/api/v1/test")
async def test_endpoint():
    return {
        "message": "API is working!",
        "azure_configured": bool(os.getenv("AZURE_CV_KEY")),
        "database_url": bool(os.getenv("DATABASE_URL"))
    }