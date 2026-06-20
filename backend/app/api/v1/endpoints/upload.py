import os
import re
import tempfile
import uuid
from datetime import datetime, timezone
from typing import BinaryIO

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, Response, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.v1.deps import DBSession, SuperAdmin
from app.core.config import settings
from app.models.image import Image
from app.services.object_storage import ensure_local_upload_dir, storage

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = os.path.join("uploads", "images")
CHUNK_SIZE = 1024 * 1024
SVG_MAX_BYTES = 5 * 1024 * 1024


class ImageUpdate(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)


IMAGE_SIGNATURES = {
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
    b"GIF87a": "image/gif",
    b"GIF89a": "image/gif",
    b"RIFF": "image/webp",
}

MIME_EXTENSIONS = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/svg+xml": "svg",
    "video/mp4": "mp4",
    "video/webm": "webm",
    "video/quicktime": "mov",
    "video/x-matroska": "mkv",
}

ALLOWED_EXTENSIONS = set(MIME_EXTENSIONS.values()) | {"jpeg"}

SVG_DANGEROUS_PATTERNS = [
    re.compile(r"<\s*script", re.IGNORECASE),
    re.compile(r"on\w+\s*=", re.IGNORECASE),
    re.compile(r"<\s*iframe", re.IGNORECASE),
    re.compile(r"<\s*embed", re.IGNORECASE),
    re.compile(r"<\s*object", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"vbscript\s*:", re.IGNORECASE),
    re.compile(r"<\s*use\s+[^>]*href\s*=\s*[\"']data:", re.IGNORECASE),
]


def _normalize_mime(content_type: str | None) -> str:
    return (content_type or "application/octet-stream").split(";", 1)[0].strip().lower()


def _media_kind(mime_type: str) -> str:
    if mime_type.startswith("video/"):
        return "video"
    return "image"


def _validate_svg(content: bytes) -> bool:
    try:
        text = content.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return False
    return not any(pattern.search(text) for pattern in SVG_DANGEROUS_PATTERNS)


def _check_magic_bytes(head: bytes, declared_mime: str, temp_path: str, size: int) -> bool:
    if not head:
        return False

    if declared_mime == "image/svg+xml":
        if size > SVG_MAX_BYTES:
            raise HTTPException(status_code=413, detail="SVG files must be 5MB or smaller")
        with open(temp_path, "rb") as f:
            content = f.read()
        return content.strip().startswith(b"<") and _validate_svg(content)

    for sig, mime in IMAGE_SIGNATURES.items():
        if head.startswith(sig):
            if mime == "image/webp":
                return declared_mime == "image/webp" and b"WEBP" in head[:12]
            return mime == declared_mime

    if declared_mime in {"video/mp4", "video/quicktime"}:
        return len(head) >= 12 and head[4:8] == b"ftyp"

    if declared_mime in {"video/webm", "video/x-matroska"}:
        return head.startswith(b"\x1a\x45\xdf\xa3")

    return False


async def _stream_to_temp(file: UploadFile) -> tuple[str, int, bytes]:
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    tmp = tempfile.NamedTemporaryFile(delete=False)
    temp_path = tmp.name
    total = 0
    head = b""
    try:
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB",
                )
            if len(head) < 512:
                head += chunk[: 512 - len(head)]
            tmp.write(chunk)
    except Exception:
        tmp.close()
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise
    finally:
        tmp.close()

    if total <= 0:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    return temp_path, total, head


def _validate_file(file: UploadFile, temp_path: str, size: int, head: bytes) -> str:
    mime_type = _normalize_mime(file.content_type)
    allowed = settings.upload_allowed_types_list
    if mime_type not in allowed:
        raise HTTPException(
            status_code=415,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed)}",
        )

    if not _check_magic_bytes(head, mime_type, temp_path, size):
        raise HTTPException(
            status_code=415,
            detail="File content does not match the declared file type",
        )

    return mime_type


def _stored_name(original_name: str | None, mime_type: str) -> str:
    ext = (original_name or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        ext = MIME_EXTENSIONS.get(mime_type, "bin")
    if ext == "jpeg":
        ext = "jpg"
    return f"{uuid.uuid4().hex}.{ext}"


def _object_key(media_type: str, filename: str) -> str:
    today = datetime.now(timezone.utc).strftime("%Y/%m")
    folder = "videos" if media_type == "video" else "images"
    return f"{folder}/{today}/{filename}"


def _iter_object_response(response):
    try:
        yield from response.stream(32 * 1024)
    finally:
        response.close()
        response.release_conn()


def _parse_range(range_header: str | None, size: int) -> tuple[int, int] | None:
    if not range_header or not range_header.startswith("bytes="):
        return None
    raw_range = range_header.removeprefix("bytes=").split(",", 1)[0].strip()
    if "-" not in raw_range:
        return None
    start_text, end_text = raw_range.split("-", 1)
    try:
        if start_text == "":
            suffix = int(end_text)
            if suffix <= 0:
                return None
            start = max(size - suffix, 0)
            end = size - 1
        else:
            start = int(start_text)
            end = int(end_text) if end_text else size - 1
    except ValueError:
        return None

    if start < 0 or start >= size or end < start:
        return None
    return start, min(end, size - 1)


@router.post("")
async def upload_file(_admin: SuperAdmin, db: DBSession, file: UploadFile = File(...)):
    temp_path, size, head = await _stream_to_temp(file)
    try:
        mime_type = _validate_file(file, temp_path, size, head)
        media_type = _media_kind(mime_type)
        stored_name = _stored_name(file.filename, mime_type)
        object_key = _object_key(media_type, stored_name)

        if settings.use_minio:
            with open(temp_path, "rb") as f:
                storage.put_file(object_key, f, size, mime_type)
            img = Image(
                filename=stored_name,
                mime_type=mime_type,
                data=None,
                file_path=None,
                object_key=object_key,
                storage_backend="minio",
                media_type=media_type,
                size=size,
            )
        else:
            ensure_local_upload_dir()
            local_path = os.path.join(UPLOAD_DIR, stored_name)
            os.replace(temp_path, local_path)
            temp_path = ""
            img = Image(
                filename=stored_name,
                mime_type=mime_type,
                data=None,
                file_path=stored_name,
                object_key=None,
                storage_backend="local",
                media_type=media_type,
                size=size,
            )

        db.add(img)
        db.commit()
        db.refresh(img)

        return {
            "url": f"/upload/{img.id}",
            "filename": stored_name,
            "id": img.id,
            "size": img.size,
            "mime_type": img.mime_type,
            "media_type": img.media_type,
            "created_at": img.created_at,
        }
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/{image_id}")
def get_image(image_id: int, request: Request, db: DBSession):
    img = db.get(Image, image_id)
    if not img:
        return Response(status_code=404)

    headers = {
        "Cache-Control": "public, max-age=86400, immutable",
        "ETag": f'"{img.id}"',
        "Accept-Ranges": "bytes",
    }

    if img.storage_backend == "minio" and img.object_key:
        byte_range = _parse_range(request.headers.get("range"), img.size)
        if byte_range:
            start, end = byte_range
            length = end - start + 1
            object_response = storage.get_file(img.object_key, offset=start, length=length)
            if object_response is not None:
                range_headers = {
                    **headers,
                    "Content-Range": f"bytes {start}-{end}/{img.size}",
                    "Content-Length": str(length),
                }
                return StreamingResponse(
                    _iter_object_response(object_response),
                    status_code=206,
                    media_type=img.mime_type,
                    headers=range_headers,
                )

        object_response = storage.get_file(img.object_key)
        if object_response is not None:
            return StreamingResponse(
                _iter_object_response(object_response),
                media_type=img.mime_type,
                headers=headers,
            )

    if img.file_path:
        full_path = img.stored_path
        if os.path.isfile(full_path):
            return FileResponse(full_path, media_type=img.mime_type, headers=headers)

    if img.data:
        return Response(content=img.data, media_type=img.mime_type, headers=headers)

    return Response(status_code=404)


@router.get("")
def list_images(_admin: SuperAdmin, db: DBSession, limit: int = Query(default=200, ge=1, le=500)):
    images = list(db.scalars(select(Image).order_by(Image.created_at.desc()).limit(limit)).all())
    return [
        {
            "id": img.id,
            "filename": img.filename,
            "url": f"/upload/{img.id}",
            "size": img.size,
            "mime_type": img.mime_type,
            "media_type": img.media_type,
            "created_at": img.created_at,
        }
        for img in images
    ]


@router.delete("/{image_id}", status_code=204)
def delete_image(image_id: int, _admin: SuperAdmin, db: DBSession):
    img = db.get(Image, image_id)
    if not img:
        return Response(status_code=404)

    if img.storage_backend == "minio" and img.object_key:
        storage.remove_file(img.object_key)
    elif img.file_path:
        full_path = img.stored_path
        if os.path.isfile(full_path):
            os.remove(full_path)

    db.delete(img)
    db.commit()


@router.put("/{image_id}")
def update_image(image_id: int, body: ImageUpdate, _admin: SuperAdmin, db: DBSession):
    img = db.get(Image, image_id)
    if not img:
        return Response(status_code=404)
    img.filename = body.filename
    db.commit()
    db.refresh(img)
    return {
        "id": img.id,
        "filename": img.filename,
        "url": f"/upload/{img.id}",
        "size": img.size,
        "mime_type": img.mime_type,
        "media_type": img.media_type,
        "created_at": img.created_at,
    }
