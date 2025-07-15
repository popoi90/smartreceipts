from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
import aiofiles
from typing import Optional

router = APIRouter(prefix="/api/v1/receipts", tags=["receipts"])

# Allowed file types
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".tiff", ".bmp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload")
async def upload_receipt(
        file: UploadFile = File(...),
        client_id: Optional[str] = None
):
    """Upload a receipt image for OCR processing"""

    # Validate file type
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_extension} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB"
        )

    # Generate unique filename
    receipt_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{receipt_id}_{timestamp}{file_extension}"

    # Create storage directory
    storage_dir = "/app/storage/receipts"
    os.makedirs(storage_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(storage_dir, filename)
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(contents)

    return {
        "receipt_id": receipt_id,
        "filename": filename,
        "original_filename": file.filename,
        "file_size": len(contents),
        "file_path": file_path,
        "status": "uploaded",
        "message": "Receipt uploaded successfully"
    }


@router.get("/test-upload")
async def test_upload_endpoint():
    """Test endpoint to verify upload router is working"""
    return {"message": "Upload endpoint is working!"}