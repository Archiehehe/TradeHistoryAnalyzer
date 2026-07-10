from urllib.parse import urljoin

import boto3

from app.core.config import Settings
from app.storage.base import StoredFile


class R2Storage:
    def __init__(self, settings: Settings):
        endpoint_url = f"https://{settings.r2_account_id}.r2.cloudflarestorage.com"
        self.bucket_name = settings.r2_bucket_name or ""
        self.public_base_url = str(settings.r2_public_base_url) if settings.r2_public_base_url else None
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=settings.r2_access_key_id.get_secret_value() if settings.r2_access_key_id else None,
            aws_secret_access_key=settings.r2_secret_access_key.get_secret_value() if settings.r2_secret_access_key else None,
            region_name="auto",
        )

    def save_bytes(self, upload_id: str, filename: str, file_bytes: bytes) -> StoredFile:
        object_key = f"uploads/{upload_id}/{filename}"
        self.client.put_object(Bucket=self.bucket_name, Key=object_key, Body=file_bytes)
        if self.public_base_url:
            storage_path = urljoin(f"{self.public_base_url.rstrip('/')}/", object_key)
        else:
            storage_path = f"r2://{self.bucket_name}/{object_key}"
        suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
        return StoredFile(filename=filename, storage_path=storage_path, file_type=suffix)

