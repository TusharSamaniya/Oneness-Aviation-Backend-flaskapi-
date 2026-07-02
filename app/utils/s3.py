import boto3
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from botocore.exceptions import ClientError

from app.config import settings

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE_MB = 10


def _get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.AWS_S3_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


async def upload_image(file: UploadFile, folder: str = "general") -> str:
    """Upload an image to S3 and return the public URL."""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file.content_type}' not allowed. Use JPEG, PNG, or WebP.",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB.")

    ext = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    key = f"{folder}/{uuid.uuid4().hex}{ext}"

    try:
        s3 = _get_s3_client()
        s3.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=key,
            Body=contents,
            ContentType=file.content_type,
            ACL="public-read",
        )
    except ClientError as e:
        raise HTTPException(status_code=502, detail=f"File upload failed: {str(e)}")

    return f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{key}"


async def delete_file(url: str) -> None:
    """Delete a file from S3 by its public URL."""
    try:
        key = url.split(".amazonaws.com/")[-1]
        s3 = _get_s3_client()
        s3.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=key)
    except Exception:
        pass  # Best-effort deletion
