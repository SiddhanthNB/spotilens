from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.models.base_model import BaseModel
from sqlalchemy import Column, Text, Integer, JSON, DateTime

class Artist(BaseModel):
    __tablename__ = "spotilens__artists"

    artist_id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    popularity = Column(Integer, nullable=True)
    followers = Column(Integer, nullable=True)
    genres = Column(JSON, nullable=True)
    images = Column(JSON, nullable=True)
    external_url = Column(Text, nullable=True)
    href = Column(Text, nullable=True)
    uri = Column(Text, nullable=True)
    type = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

    albums = relationship("Album", secondary="spotilens__album_artists", back_populates="artists")
    tracks = relationship("Track", secondary="spotilens__track_artists", back_populates="artists")
