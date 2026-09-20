import io
import logging
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
from app.services.object_storage import ensure_local_upload_dir, get_object_storage

logger = logging.getLogger("blog")

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = os.path.join("uploads", "images")

# Image compression settings
MAX_IMAGE_DIMENSION = 1920       # Max width/height in pixels
IMAGE_QUALITY = 85               # JPEG/WebP quality (1-100)
AVATAR_MAX_DIMENSION = 512       # Avatars are smaller
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
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/aac": "aac",
    "audio/x-m4a": "m4a",
    "audio/mp4": "m4a",
    "audio/ogg": "ogg",
    "audio/webm": "weba",
    "audio/flac": "flac",
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
    if mime_type.startswith("audio/"):
        return "music"
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

    # 音频文件魔数校验
    if declared_mime == "audio/mpeg" or declared_mime == "audio/mp3":
        return head.startswith(b"\xff\xfb") or head.startswith(b"\xff\xf3") or head.startswith(b"\xff\xf2") or head.startswith(b"ID3")
    if declared_mime in {"audio/wav", "audio/x-wav"}:
        return head.startswith(b"RIFF") and b"WAVE" in head[:12]
    if declared_mime in {"audio/aac", "audio/mp4", "audio/x-m4a"}:
        # m4a/aac 容器：ftyp box 在 offset 4，或 ADTS 原始流以 \xff\xf1/\xff\xf9 开头
        return head.startswith(b"\xff\xf1") or head.startswith(b"\xff\xf9") or head[4:8] == b"ftyp"
    if declared_mime == "audio/ogg":
        return head.startswith(b"OggS")
    if declared_mime == "audio/webm":
        return head.startswith(b"\x1a\x45\xdf\xa3")
    if declared_mime == "audio/flac":
        return head.startswith(b"fLaC")

    return False


def _compress_image(temp_path: str, mime_type: str, max_dim: int = MAX_IMAGE_DIMENSION) -> tuple[str, int, str]:
    """Compress and resize an image using Pillow.

    Returns (path, new_size, new_mime_type).
    If Pillow is not available or image is not processable, returns original.
    """
    try:
        from PIL import Image as PILImage
    except ImportError:
        return temp_path, os.path.getsize(temp_path), mime_type

    try:
        img = PILImage.open(temp_path)

        # Strip EXIF rotation but keep quality
        from PIL import ImageOps
        img = ImageOps.exif_transpose(img)

        # Convert RGBA/P to RGB for JPEG
        if img.mode in ("RGBA", "P", "LA"):
            bg = PILImage.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
            img = bg

        # Resize if exceeds max dimension
        w, h = img.size
        if max(w, h) > max_dim:
            ratio = max_dim / max(w, h)
            img = img.resize((int(w * ratio), int(h * ratio)), PILImage.LANCZOS)

        # Save compressed
        buf = io.BytesIO()
        # Always output JPEG for photos (smaller than PNG for photos)
        output_mime = "image/jpeg"
        ext = "jpg"
        img.save(buf, format="JPEG", quality=IMAGE_QUALITY, optimize=True)
        new_data = buf.getvalue()
        new_size = len(new_data)

        # Overwrite temp file
        with open(temp_path, "wb") as f:
            f.write(new_data)

        logger.info("Image compressed: %dx%d → %dx%d, %d → %d bytes",
                    w, h, img.size[0], img.size[1], os.path.getsize(temp_path), new_size)
        return temp_path, new_size, output_mime

    except Exception as e:
        logger.warning("Image compression failed (using original): %s", e)
        return temp_path, os.path.getsize(temp_path), mime_type


async def _stream_to_temp(file: UploadFile) -> tuple[str, int, bytes]:
    declared_mime = _normalize_mime(file.content_type)
    # 视频单独限制 100MB（2G 服务器内存瓶颈）
    if declared_mime.startswith("video/"):
        max_bytes = 100 * 1024 * 1024
    else:
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
                if declared_mime.startswith("video/"):
                    raise HTTPException(
                        status_code=413,
                        detail="视频文件不能超过 100MB",
                    )
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
    if media_type == "video":
        folder = "videos"
    elif media_type == "music":
        folder = "music"
    elif media_type == "audio":
        folder = "audios"
    else:
        folder = "images"
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

        # Auto-compress images
        if media_type == "image":
            temp_path, size, mime_type = _compress_image(temp_path, mime_type)

        stored_name = _stored_name(file.filename, mime_type)
        object_key = _object_key(media_type, stored_name)
        original_name = file.filename or stored_name  # 保留原始文件名（中文）
        uploader_label = f"{_admin.username}_{_admin.email or 'no-email'}"

        if settings.use_minio:
            obj_store = get_object_storage()
            if obj_store:
                with open(temp_path, "rb") as f:
                    obj_store.put_file(object_key, f, size, mime_type)
            img = Image(
                filename=original_name,
                mime_type=mime_type,
                data=None,
                file_path=None,
                object_key=object_key,
                storage_backend="minio",
                media_type=media_type,
                size=size,
                uploaded_by=uploader_label,
            )
        else:
            ensure_local_upload_dir()
            # Organize by user folder
            user_upload_dir = os.path.join(UPLOAD_DIR, uploader_label)
            os.makedirs(user_upload_dir, exist_ok=True)
            local_path = os.path.join(user_upload_dir, stored_name)
            os.replace(temp_path, local_path)
            temp_path = ""
            img = Image(
                filename=original_name,
                mime_type=mime_type,
                data=None,
                file_path=f"{uploader_label}/{stored_name}",
                object_key=None,
                storage_backend="local",
                media_type=media_type,
                size=size,
                uploaded_by=uploader_label,
            )

        db.add(img)
        db.commit()
        db.refresh(img)

        return {
            "url": f"/api/v1/upload/{img.id}",
            "filename": original_name,
            "id": img.id,
            "size": img.size,
            "mime_type": img.mime_type,
            "media_type": img.media_type,
            "uploaded_by": uploader_label,
            "created_at": img.created_at,
        }
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/music")
def list_music(db: DBSession, limit: int = Query(default=50, ge=1, le=200)):
    """公开接口 — 获取音乐列表（无需登录）"""
    images = list(db.scalars(
        select(Image).where(Image.media_type == "music").order_by(Image.created_at.desc()).limit(limit)
    ).all())
    return [
        {
            "id": img.id,
            "filename": img.filename,
            "url": f"/api/v1/upload/{img.id}",
        }
        for img in images
    ]


@router.get("/{image_id}")
@router.head("/{image_id}")
def get_image(image_id: int, request: Request, db: DBSession):
    img = db.get(Image, image_id)
    if not img:
        return Response(status_code=404)

    headers = {
        "Cache-Control": "public, max-age=86400, immutable",
        "ETag": f'"{img.id}"',
        "Accept-Ranges": "bytes",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
    }
    # SVG 文件额外加 CSP 阻止脚本执行，强制下载（防存储型 XSS）
    if img.mime_type == "image/svg+xml":
        headers["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'"
        headers["Content-Disposition"] = 'attachment; filename="image.svg"'

    if img.storage_backend == "minio" and img.object_key:
        byte_range = _parse_range(request.headers.get("range"), img.size)
        if byte_range:
            start, end = byte_range
            length = end - start + 1
            object_response = None
            obj_store = get_object_storage()
            if obj_store:
                object_response = obj_store.get_file(img.object_key, offset=start, length=length)
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

        obj_store = get_object_storage()
        if obj_store:
            object_response = obj_store.get_file(img.object_key)
        else:
            object_response = None
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
            "url": f"/api/v1/upload/{img.id}",
            "size": img.size,
            "mime_type": img.mime_type,
            "media_type": img.media_type,
            "uploaded_by": img.uploaded_by or "unknown",
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
        obj_store = get_object_storage()
        if obj_store:
            obj_store.remove_file(img.object_key)
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
        "url": f"/api/v1/upload/{img.id}",
        "size": img.size,
        "mime_type": img.mime_type,
        "media_type": img.media_type,
        "created_at": img.created_at,
    }
