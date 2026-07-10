from dataclasses import dataclass


@dataclass(slots=True)
class StoredFile:
    filename: str
    storage_path: str
    file_type: str

