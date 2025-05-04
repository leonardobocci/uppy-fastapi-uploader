import os
import uuid
from pathlib import Path
from typing import Any, Annotated

from fastapi import APIRouter, HTTPException, UploadFile, status, Form

from app.api.deps import CurrentUser
from app.core.config import settings
from app.models import Message
import datetime as dt

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
    file: UploadFile,
    current_user: CurrentUser,
    file_datetime: Annotated[str, Form()]
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

    # Assign random uuid instead of filename and save in timestamped directory
    extension = Path(file.filename).suffix.lower()
    safe_filename = f"{uuid.uuid4()}{extension}"
    file_date = dt.datetime.fromisoformat(file_datetime)
    directory = os.path.join(
        Path().resolve(), settings.UPLOAD_DIR, str(current_user.id), str(round(file_date.timestamp()))
    )
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, safe_filename)

    # Save file to disk
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    return Message(message="Files uploaded successfully")
