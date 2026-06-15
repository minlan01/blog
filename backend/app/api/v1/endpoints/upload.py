import os
import re
import uuid

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.v1.deps import DBSession, SuperAdmin
from app.core.config import settings
from app.models.image import Image

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = os.path.join("uploads", "images")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ImageUpdate(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)

FILE_SIGNATURES = {
    b'\x89PNG\r\n\x1a\n': 'image/png',
    b'\xff\xd8\xff': 'image/jpeg',
    b'GIF87a': 'image/gif',
    b'GIF89a': 'image/gif',
    b'RIFF': 'image/webp',
}

SVG_DANGEROUS_PATTERNS = [
    re.compile(r'<\s*script', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),
    re.compile(r'<\s*iframe', re.IGNORECASE),
    re.compile(r'<\s*embed', re.IGNORECASE),
    re.compile(r'<\s*object', re.IGNORECASE),
    re.compile(r'javascript\s*:', re.IGNORECASE),
    re.compile(r'vbscript\s*:', re.IGNORECASE),
    re.compile(r'<\s*use\s+[^>]*href\s*=\s*["\']data:', re.IGNORECASE),
]


def _validate_svg(content: bytes) -> bool:
    try:
        text = content.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return False
    for pattern in SVG_DANGEROUS_PATTERNS:
        if pattern.search(text):
            return False
    return True


def _validate_file(file: UploadFile, content: bytes) -> None:
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    allowed = settings.upload_allowed_types_list
    if file.content_type not in allowed:
        raise HTTPException(
            status_code=415,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed)}",
        )

    if not _check_magic_bytes(content, file.content_type):
        raise HTTPException(
            status_code=415,
            detail="File content does not match the declared file type",
        )


def _check_magic_bytes(content: bytes, declared_mime: str) -> bool:
    if not content:
        return False

    if declared_mime == 'image/svg+xml':
        return content.strip().startswith(b'<') and _validate_svg(content)

    for sig, mime in FILE_SIGNATURES.items():
        if content.startswith(sig):
            if mime == declared_mime:
                return True
            if mime == 'image/jpeg' and declared_mime == 'image/jpeg':
                return True

    if declared_mime == 'image/webp' and content.startswith(b'RIFF'):
        if b'WEBP' in content[:12]:
            return True

    return False


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg"}


@router.post("")
async def upload_file(_admin: SuperAdmin, db: DBSession, file: UploadFile = File(...)):
    content = await file.read()

    _validate_file(file, content)

    ext = (file.filename or "image.png").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        ext = "png"
    stored_name = f"{uuid.uuid4().hex}.{ext}"

    file_path = os.path.join(UPLOAD_DIR, stored_name)
    with open(file_path, "wb") as f:
        f.write(content)

    img = Image(
        filename=stored_name,
        mime_type=file.content_type or "application/octet-stream",
        data=None,
        file_path=stored_name,
        size=len(content),
    )
    db.add(img)
    db.commit()
    db.refresh(img)

    return {"url": f"/upload/{img.id}", "filename": stored_name, "id": img.id}


@router.get("/{image_id}")
def get_image(image_id: int, db: DBSession):
    img = db.get(Image, image_id)
    if not img:
        return Response(status_code=404)

    if img.file_path:
        full_path = img.stored_path
        if os.path.isfile(full_path):
            return FileResponse(
                full_path,
                media_type=img.mime_type,
                headers={
                    "Cache-Control": "public, max-age=86400, immutable",
                    "ETag": f'"{img.id}"',
                },
            )

    if img.data:
        return Response(
            content=img.data,
            media_type=img.mime_type,
            headers={
                "Cache-Control": "public, max-age=86400, immutable",
                "ETag": f'"{img.id}"',
            },
        )

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
            "created_at": img.created_at,
        }
        for img in images
    ]


@router.delete("/{image_id}", status_code=204)
def delete_image(image_id: int, _admin: SuperAdmin, db: DBSession):
    img = db.get(Image, image_id)
    if not img:
        return Response(status_code=404)
    if img.file_path:
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
    return {"id": img.id, "filename": img.filename, "url": f"/upload/{img.id}", "size": img.size}
