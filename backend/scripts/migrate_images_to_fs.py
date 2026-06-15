"""Migrate existing DB BLOB images to filesystem storage.

Usage:
    cd backend
    python -m scripts.migrate_images_to_fs
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.models.image import Image

UPLOAD_DIR = os.path.join("uploads", "images")


def main():
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    db = SessionLocal()
    try:
        images = db.query(Image).filter(Image.data.isnot(None), Image.file_path.is_(None)).all()
        if not images:
            print("No images to migrate.")
            return

        migrated = 0
        for img in images:
            if not img.data:
                continue

            ext = img.filename.rsplit(".", 1)[-1].lower() if "." in img.filename else "png"
            stored_name = img.filename if img.filename else f"{img.id}.{ext}"
            full_path = os.path.join(UPLOAD_DIR, stored_name)

            if os.path.exists(full_path):
                base, ext_part = stored_name.rsplit(".", 1) if "." in stored_name else (stored_name, "bin")
                stored_name = f"{base}_{img.id}.{ext_part}"
                full_path = os.path.join(UPLOAD_DIR, stored_name)

            with open(full_path, "wb") as f:
                f.write(img.data)

            img.file_path = stored_name
            img.data = None
            migrated += 1
            print(f"  [{migrated}/{len(images)}] Image {img.id} → {full_path}")

        db.commit()
        print(f"\nDone: migrated {migrated} images to filesystem.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
