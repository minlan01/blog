from __future__ import annotations

import os
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from app.core.config import settings


class ObjectStorage:
    def __init__(self) -> None:
        self._client: Minio | None = None

    @property
    def client(self) -> Minio:
        if self._client is None:
            self._client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )
        return self._client

    def ensure_bucket(self) -> None:
        if not settings.use_minio:
            return
        if not self.client.bucket_exists(settings.MINIO_BUCKET):
            self.client.make_bucket(settings.MINIO_BUCKET)

    def put_file(
        self,
        object_name: str,
        file_data: BinaryIO,
        size: int,
        content_type: str,
    ) -> None:
        self.ensure_bucket()
        self.client.put_object(
            settings.MINIO_BUCKET,
            object_name,
            file_data,
            length=size,
            content_type=content_type,
        )

    def get_file(self, object_name: str, offset: int = 0, length: int = 0):
        try:
            return self.client.get_object(
                settings.MINIO_BUCKET,
                object_name,
                offset=offset,
                length=length,
            )
        except S3Error as exc:
            if exc.code in {"NoSuchKey", "NoSuchBucket"}:
                return None
            raise

    def remove_file(self, object_name: str) -> None:
        try:
            self.client.remove_object(settings.MINIO_BUCKET, object_name)
        except S3Error as exc:
            if exc.code not in {"NoSuchKey", "NoSuchBucket"}:
                raise


storage = ObjectStorage()


def ensure_local_upload_dir() -> None:
    os.makedirs(os.path.join("uploads", "images"), exist_ok=True)
