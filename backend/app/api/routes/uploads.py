import uuid
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.deps import CurrentUser
from app.core.config import settings
from app.models import Message

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_EXTENSIONS = [
    ".parquet",
    ".csv",
    ".json",
    ".xml",
    ".txt",
    ".xlsx",
    ".xls",
    ".xlsb",
    ".xlsm",
]


def validate_file_extension(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


@router.post("/", response_model=Message)
async def upload_files(
    current_user: CurrentUser,
    files: Annotated[list[UploadFile], File(...)],
) -> Any:
    """
    Upload multiple files with security checks.
    """
    # Create user-specific upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR) / str(current_user.id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        # Validate file extension
        if not validate_file_extension(file.filename):
            raise HTTPException(
                status_code=400, detail=f"File extension not allowed: {file.filename}"
            )

        # Generate safe filename
        ext = Path(file.filename).suffix.lower()
        safe_filename = f"{uuid.uuid4()}{ext}"
        file_path = upload_dir / safe_filename

        # Save file to disk
        try:
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    return Message(message="Files uploaded successfully")
