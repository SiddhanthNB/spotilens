from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.models.base_model import BaseModel
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, UniqueConstraint

class ListeningHistory(BaseModel):
    __tablename__ = "spotilens__listening_history"
    __table_args__ = ( UniqueConstraint("track_id", "played_at", name="uq_track_played_at"), )

    play_id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(Text, ForeignKey("spotilens__tracks.track_id"), nullable=False)
    track_name = Column(Text, nullable=True)
    context_type = Column(Text, nullable=True)
    context_uri = Column(Text, nullable=True)
    record_type = Column(Text, nullable=False)  # 'historical-data' or 'daily-sync'
    played_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

    track = relationship("Track", back_populates="plays")
