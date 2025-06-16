from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.sql import func
from db.models.base_model import BaseModel

class SyncLog(BaseModel):
    __tablename__ = "spotilens__sync_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sync_source = Column(Text, nullable=False)  # e.g., 'recently-played-api'
    status = Column(Text, nullable=False)       # e.g., 'success', 'error'
    response = Column(Text, nullable=True)      # any additional info or error message
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)
