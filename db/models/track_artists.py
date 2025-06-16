from sqlalchemy.sql import func
from db.models.base_model import BaseModel
from sqlalchemy import Column, Text, DateTime, ForeignKey, PrimaryKeyConstraint

class TrackArtist(BaseModel):
    __tablename__ = "spotilens__track_artists"

    __table_args__ = ( PrimaryKeyConstraint('track_id', 'artist_id'), )

    track_id = Column(Text, ForeignKey("spotilens__tracks.track_id"), nullable=False)
    artist_id = Column(Text, ForeignKey("spotilens__artists.artist_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)