from __future__ import annotations

import os
from typing import TYPE_CHECKING, BinaryIO, Optional

from app.core.config import settings


class ObjectStorage:
    """Object storage wrapper supporting S3-compatible backends.

    Uses boto3 which is compatible with Aliyun OSS, AWS S3, MinIO, etc.
    Only loaded when STORAGE_BACKEND != 'local'.
    """

    def __init__(self) -> None:
        self._client = None

    @property
    def client(self):
        if self._client is None:
            import boto3  # lazy import
            from botocore.config import Config as BotoConfig

            # Parse endpoint: strip protocol if present
            endpoint = settings.MINIO_ENDPOINT
            if not endpoint.startswith("http"):
                scheme = "https" if settings.MINIO_SECURE else "http"
                endpoint = f"{scheme}://{endpoint}"

            self._client = boto3.client(
                "s3",
                endpoint_url=endpoint,
                aws_access_key_id=settings.MINIO_ACCESS_KEY,
                aws_secret_access_key=settings.MINIO_SECRET_KEY,
                region_name="us-east-1",
                config=BotoConfig(
                    signature_version="s3v4",
                    s3={
                        "addressing_style": "virtual",
                    },
                    retries={"max_attempts": 3, "mode": "standard"},
                ),
            )
        return self._client

    def ensure_bucket(self) -> None:
        if not settings.use_minio:
            return
        try:
            self.client.head_bucket(Bucket=settings.MINIO_BUCKET)
        except Exception:
            # Bucket doesn't exist or can't access - create it
            try:
                self.client.create_bucket(Bucket=settings.MINIO_BUCKET)
            except Exception:
                pass  # OSS may auto-create; errors are non-fatal

    def put_file(
        self,
        object_name: str,
        file_data: BinaryIO,
        size: int,
        content_type: str,
    ) -> None:
        self.ensure_bucket()
        # Read full data into bytes
        if hasattr(file_data, "read"):
            body = file_data.read()
        else:
            body = file_data
        # Calculate SHA256 to force content-based signing (avoids streaming trailer)
        import hashlib
        import base64
        sha256 = hashlib.sha256(body).digest()
        sha256_b64 = base64.b64encode(sha256).decode()
        self.client.put_object(
            Bucket=settings.MINIO_BUCKET,
            Key=object_name,
            Body=body,
            ContentLength=len(body),
            ContentType=content_type,
            ChecksumSHA256=sha256_b64,
        )

    def get_file(self, object_name: str, offset: int = 0, length: int = 0):
        """Get file from storage. Returns a response object with .stream() method."""
        from types import SimpleNamespace

        kwargs = {"Bucket": settings.MINIO_BUCKET, "Key": object_name}
        if offset > 0 or length > 0:
            end = offset + length - 1 if length > 0 else ""
            kwargs["Range"] = f"bytes={offset}-{end}"

        try:
            response = self.client.get_object(**kwargs)
        except Exception:
            return None

        # Wrap to match the old minio response interface
        class _StreamWrapper:
            def __init__(self, body):
                self._body = body

            def stream(self, chunk_size):
                yield from self._body.iter_chunks(chunk_size)

            def read(self):
                return self._body.read()

            def close(self):
                self._body.close()

            def release_conn(self):
                pass

        return _StreamWrapper(response["Body"])

    def remove_file(self, object_name: str) -> None:
        try:
            self.client.delete_object(Bucket=settings.MINIO_BUCKET, Key=object_name)
        except Exception:
            pass  # Non-fatal


# Module-level singleton
_storage: Optional[ObjectStorage] = None


def get_object_storage() -> Optional[ObjectStorage]:
    """Return ObjectStorage instance if configured, else None."""
    global _storage
    if not settings.use_minio:
        return None
    if _storage is None:
        _storage = ObjectStorage()
    return _storage


def ensure_local_upload_dir() -> None:
    os.makedirs(os.path.join("uploads", "images"), exist_ok=True)
