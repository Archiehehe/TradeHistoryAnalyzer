from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database_configured: bool
    environment: str

