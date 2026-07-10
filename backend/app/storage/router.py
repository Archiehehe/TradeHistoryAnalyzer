from app.core.config import Settings
from app.storage.local import LocalStorage
from app.storage.r2 import R2Storage


def get_storage_backend(settings: Settings):
    if settings.r2_configured:
        return R2Storage(settings)
    return LocalStorage(settings.local_storage_root)

