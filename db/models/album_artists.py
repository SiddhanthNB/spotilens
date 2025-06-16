from sqlalchemy.sql import func
from db.models.base_model import BaseModel
from sqlalchemy import Column, Text, DateTime, ForeignKey, PrimaryKeyConstraint

class AlbumArtist(BaseModel):
    __tablename__ = "spotilens__album_artists"

    __table_args__ = ( PrimaryKeyConstraint('album_id', 'artist_id'), )

    album_id = Column(Text, ForeignKey("spotilens__albums.album_id"), nullable=False)
    artist_id = Column(Text, ForeignKey("spotilens__artists.artist_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)
