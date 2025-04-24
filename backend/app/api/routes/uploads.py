import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile, status

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
    ".avro",
    ".orc",
]


def validate_file_extension(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


@router.post("/", response_model=Message, status_code=status.HTTP_201_CREATED)
async def upload_files(
    current_user: CurrentUser,
    file: UploadFile,
) -> Any:
    """
    Validate and save an uploaded file.
    """

    if not file:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No file was uploaded",
        )

    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=415, detail=f"File extension not allowed: {file.filename}"
        )

    # Assign random uuid instead of filename
    extension = Path(file.filename).suffix.lower()
    safe_filename = f"{uuid.uuid4()}{extension}"
    file_path = Path().resolve() / Path(settings.UPLOAD_DIR) / safe_filename

    # Save file to disk
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    return Message(message="Files uploaded successfully")
