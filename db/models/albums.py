from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.models.base_model import BaseModel
from sqlalchemy import Column, Text, Integer, DateTime, JSON, ForeignKey

class Album(BaseModel):
    __tablename__ = "spotilens__albums"

    album_id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    album_type = Column(Text, nullable=True)
    release_date = Column(Text, nullable=True)
    release_precision = Column(Text, nullable=True)
    total_tracks = Column(Integer, nullable=True)
    genres = Column(JSON, nullable=True)
    label = Column(Text, nullable=True)
    popularity = Column(Integer, nullable=True)
    images = Column(JSON, nullable=True)
    external_url = Column(Text, nullable=True)
    href = Column(Text, nullable=True)
    uri = Column(Text, nullable=True)
    type = Column(Text, nullable=True)
    artist_id = Column(Text, ForeignKey("spotilens__artists.artist_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

    artist = relationship("Artist", back_populates="albums")
    tracks = relationship("Track", back_populates="album", cascade="all, delete-orphan")
