from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.models.base_model import BaseModel
from sqlalchemy import Column, Text, Integer, Boolean, DateTime, JSON, ForeignKey

class Track(BaseModel):
    __tablename__ = "spotilens__tracks"

    track_id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    duration_ms = Column(Integer, nullable=True)
    explicit = Column(Boolean, nullable=True)
    popularity = Column(Integer, nullable=True)
    disc_number = Column(Integer, nullable=True)
    track_number = Column(Integer, nullable=True)
    is_playable = Column(Boolean, nullable=True)
    preview_url = Column(Text, nullable=True)
    external_url = Column(Text, nullable=True)
    href = Column(Text, nullable=True)
    uri = Column(Text, nullable=True)
    type = Column(Text, nullable=True)
    album_id = Column(Text, ForeignKey("spotilens__albums.album_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

    album = relationship("Album", back_populates="tracks")
    artists = relationship("Artist", secondary="spotilens__track_artists", back_populates="tracks")
    plays = relationship("ListeningHistory", back_populates="track", cascade="all, delete-orphan")
