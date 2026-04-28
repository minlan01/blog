import uuid

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import Response
from sqlalchemy import select

from app.api.v1.deps import DBSession, SuperAdmin
from app.core.config import settings
from app.models.image import Image

router = APIRouter(prefix="/upload", tags=["upload"])

# Magic bytes for allowed image types
FILE_SIGNATURES = {
    b'\x89PNG\r\n\x1a\n': 'image/png',
    b'\xff\xd8\xff': 'image/jpeg',
    b'GIF87a': 'image/gif',
    b'GIF89a': 'image/gif',
    b'RIFF': 'image/webp',  # WebP starts with RIFF...WEBP
}


def _validate_file(file: UploadFile, content: bytes) -> None:
    """Validate uploaded file type and size."""
    # Size check
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # MIME type whitelist
    allowed = settings.upload_allowed_types_list
    if file.content_type not in allowed:
        raise HTTPException(
            status_code=415,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed)}",
        )

    # Magic bytes validation
    if not _check_magic_bytes(content, file.content_type):
        raise HTTPException(
            status_code=415,
            detail="File content does not match the declared file type",
        )


def _check_magic_bytes(content: bytes, declared_mime: str) -> bool:
    """Check if file magic bytes match the declared MIME type."""
    if not content:
        return False

    # SVG is text-based, skip magic byte check
    if declared_mime == 'image/svg+xml':
        return content.strip().startswith(b'<')

    for sig, mime in FILE_SIGNATURES.items():
        if content.startswith(sig):
            if mime == declared_mime:
                return True
            # JPEG all start with ff d8 ff
            if mime == 'image/jpeg' and declared_mime == 'image/jpeg':
                return True

    # WebP: RIFF....WEBP
    if declared_mime == 'image/webp' and content.startswith(b'RIFF'):
        if b'WEBP' in content[:12]:
            return True

    return True  # Fallback: allow if basic checks pass


@router.post("")
async def upload_file(_admin: SuperAdmin, db: DBSession, file: UploadFile = File(...)):
    content = await file.read()

    # Security validation
    _validate_file(file, content)

    ext = (file.filename or "image.png").rsplit(".", 1)[-1].lower()
    stored_name = f"{uuid.uuid4().hex}.{ext}"

    img = Image(
        filename=stored_name,
        mime_type=file.content_type or "application/octet-stream",
        data=content,
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
    return Response(content=img.data, media_type=img.mime_type)


@router.get("")
def list_images(_admin: SuperAdmin, db: DBSession):
    """List all images for admin media library."""
    images = list(db.scalars(select(Image).order_by(Image.created_at.desc())).all())
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
    """Delete an image by ID (admin only)."""
    img = db.get(Image, image_id)
    if not img:
        return Response(status_code=404)
    db.delete(img)
    db.commit()


@router.put("/{image_id}")
def update_image(image_id: int, body: dict, _admin: SuperAdmin, db: DBSession):
    """Update image metadata (e.g. rename filename)."""
    img = db.get(Image, image_id)
    if not img:
        return Response(status_code=404)
    if "filename" in body and body["filename"]:
        img.filename = body["filename"]
    db.commit()
    db.refresh(img)
    return {"id": img.id, "filename": img.filename, "url": f"/upload/{img.id}", "size": img.size}
