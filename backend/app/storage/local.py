from pathlib import Path
import re

from app.storage.base import StoredFile


class LocalStorage:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save_bytes(self, upload_id: str, filename: str, file_bytes: bytes) -> StoredFile:
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", filename)
        directory = self.root / upload_id
        directory.mkdir(parents=True, exist_ok=True)
        destination = directory / safe_name
        destination.write_bytes(file_bytes)
        suffix = destination.suffix.lower().lstrip(".") or "bin"
        return StoredFile(filename=filename, storage_path=str(destination), file_type=suffix)

