from config.logger import logger
from typing import Dict, List, Optional, Any
from datetime import datetime

from db.models.artists import Artist
from db.models.albums import Album
from db.models.tracks import Track
from db.models.album_artists import AlbumArtist
from db.models.track_artists import TrackArtist
from db.models.listening_history import ListeningHistory

def store_spotify_track_in_db(payload: Dict[str, Any], record_type: Optional[str] = 'daily-sync') -> ListeningHistory:
    # Extract track.id and played_at timestamp
    track_data = payload.get('track', {})
    track_id = track_data.get('id')
    played_at_str = payload.get('played_at')

    if not track_id or not played_at_str:
        raise Exception("Missing track_id or played_at in payload")

    # Parse played_at timestamp
    played_at_dt = datetime.fromisoformat(played_at_str.replace('Z', '+00:00'))

    # Check if listening_history already has this record using track_id + timestamp
    existing_history = ListeningHistory.fetch_records(filters={'track_id': track_id, 'played_at': played_at_dt})

    if existing_history:
        logger.info(f"Skipping existing listening history for track {track_id} at {played_at_str}")
        return existing_history[0]

    # 1. Track Artists Processing (track.artists[])
    track_artists_data = track_data.get('artists', [])
    track_artist_ids = []

    for artist_data in track_artists_data:
        artist_id = artist_data.get('id')
        if not artist_id:
            continue

        artist = get_or_create_artist(artist_data)
        track_artist_ids.append(artist.artist_id)

    if not track_artist_ids:
        raise Exception(f"No valid track artists found for track {track_id} in API response")

    # 2. Album Artists Processing (track.album.artists[])
    album_data = track_data.get('album', {})
    album_artists_data = album_data.get('artists', [])
    album_artist_ids = []

    for artist_data in album_artists_data:
        artist_id = artist_data.get('id')
        if not artist_id:
            continue

        artist = get_or_create_artist(artist_data)
        album_artist_ids.append(artist.artist_id)

    if not album_artist_ids:
        raise Exception(f"No valid album artists found for track {track_id} in API response")

    # 3. Album Processing (track.album)
    album_id = album_data.get('id')
    if not album_id:
        raise Exception(f"No album ID found for track {track_id} in API response")

    album = get_or_create_album(album_data, album_artist_ids)

    # 4. Track Processing (track)
    track = get_or_create_track(track_data, album.album_id, track_artist_ids)

    # 5. Listening History Creation
    context_data = payload.get('context', {})
    listening_history = create_listening_history(
        track_id=track.track_id,
        played_at=played_at_dt,
        record_type=record_type,
        context=context_data
    )
    logger.info(f"Successfully processed track {track_id} played at {played_at_str}")

    return listening_history


def get_or_create_artist(artist_data: Dict[str, Any]) -> Artist:
    """
    Check if artist exists by spotify_id, if not create new artist record
    Returns existing or created Artist object
    """
    artist_id = artist_data.get('id')
    if not artist_id:
        raise Exception("Artist data missing ID")

    # Check if artist exists by spotify_id
    existing_artist = Artist.fetch_record_by_id(artist_id)
    if existing_artist:
        logger.info(f"Found existing artist: {existing_artist.name} ({artist_id})")
        return existing_artist

    # Create new artist record
    artist_record_data = {
        'artist_id': artist_id,
        'name': artist_data.get('name', 'Unknown Artist'),
        'popularity': artist_data.get('popularity'),
        'followers': artist_data.get('followers', {}).get('total') if artist_data.get('followers') else None,
        'genres': artist_data.get('genres', []),
        'images': artist_data.get('images', []),
        'external_url': artist_data.get('external_urls', {}).get('spotify'),
        'href': artist_data.get('href'),
        'uri': artist_data.get('uri'),
        'type': artist_data.get('type')
    }

    artist = Artist.create_record(artist_record_data)
    logger.info(f"Created new artist: {artist_data.get('name')} ({artist_id})")

    return artist


def get_or_create_album(album_data: Dict[str, Any], album_artist_ids: List[str]) -> Album:
    def associate_album_with_artist(album_id: str, artist_id: str) -> AlbumArtist:
        """
        Associate album with artist using spotilens__album_artists junction table
        Returns created AlbumArtist object or raises Exception
        """
        album_artist_data = {
            'album_id': album_id,
            'artist_id': artist_id
        }

        album_artist = AlbumArtist.create_record(album_artist_data)
        logger.info(f"Associated artist {artist_id} with album {album_id}")

        return album_artist

    album_id = album_data.get('id')
    if not album_id:
        raise Exception("Album data missing ID")

    # Check if album exists by spotify_id
    existing_album = Album.fetch_record_by_id(album_id)
    if existing_album:
        logger.info(f"Found existing album: {existing_album.name} ({album_id})")

        # Check if all artists are already associated with this album
        existing_associations = AlbumArtist.fetch_records(filters={'album_id': album_id})
        existing_artist_ids = {aa.artist_id for aa in existing_associations}
        new_artist_ids = set(album_artist_ids) - existing_artist_ids

        # Associate any new artists with existing album
        [ associate_album_with_artist(album_id, artist_id) for artist_id in new_artist_ids ]

        return existing_album

    # Create new album record
    album_record_data = {
        'album_id': album_id,
        'name': album_data.get('name', 'Unknown Album'),
        'album_type': album_data.get('album_type'),
        'release_date': album_data.get('release_date'),
        'release_precision': album_data.get('release_date_precision'),
        'total_tracks': album_data.get('total_tracks'),
        'genres': album_data.get('genres', []),
        'label': album_data.get('label'),
        'popularity': album_data.get('popularity'),
        'images': album_data.get('images', []),
        'external_url': album_data.get('external_urls', {}).get('spotify'),
        'href': album_data.get('href'),
        'uri': album_data.get('uri'),
        'type': album_data.get('type')
    }

    album = Album.create_record(album_record_data)
    logger.info(f"Created new album: {album_data.get('name')} ({album_id})")

    # Associate with album artists using spotilens__album_artists table
    [ associate_album_with_artist(album_id, artist_id) for artist_id in album_artist_ids ]

    return album


def get_or_create_track(track_data: Dict[str, Any], album_id: str, track_artist_ids: List[str]) -> Track:
    def associate_track_with_artist(track_id: str, artist_id: str) -> TrackArtist:
        """
        Associate track with artist using spotilens__track_artists junction table
        Returns created TrackArtist object or raises Exception
        """
        track_artist_data = {
            'track_id': track_id,
            'artist_id': artist_id
        }

        track_artist = TrackArtist.create_record(track_artist_data)
        logger.info(f"Associated artist {artist_id} with track {track_id}")

        return track_artist

    track_id = track_data.get('id')
    if not track_id:
        raise Exception("Track data missing ID")

    # Check if track exists by spotify_id
    existing_track = Track.fetch_record_by_id(track_id)
    if existing_track:
        logger.info(f"Found existing track: {existing_track.name} ({track_id})")

        # Check if all artists are already associated with this track
        existing_associations = TrackArtist.fetch_records(filters={'track_id': track_id})
        existing_artist_ids = {ta.artist_id for ta in existing_associations}
        new_artist_ids = set(track_artist_ids) - existing_artist_ids

        # Associate any new artists with existing track
        [ associate_track_with_artist(track_id, artist_id) for artist_id in new_artist_ids ]

        return existing_track

    # Create new track record
    track_record_data = {
        'track_id': track_id,
        'album_id': album_id,
        'name': track_data.get('name', 'Unknown Track'),
        'duration_ms': track_data.get('duration_ms'),
        'explicit': track_data.get('explicit'),
        'popularity': track_data.get('popularity'),
        'disc_number': track_data.get('disc_number'),
        'track_number': track_data.get('track_number'),
        'is_playable': track_data.get('is_playable'),
        'preview_url': track_data.get('preview_url'),
        'external_url': track_data.get('external_urls', {}).get('spotify'),
        'href': track_data.get('href'),
        'uri': track_data.get('uri'),
        'type': track_data.get('type')
    }

    track = Track.create_record(track_record_data)
    logger.info(f"Created new track: {track_data.get('name')} ({track_id})")

    # Associate with track artists using spotilens__track_artists table
    [ associate_track_with_artist(track_id, artist_id) for artist_id in track_artist_ids ]

    return track


def create_listening_history(track_id: str, played_at: datetime, record_type: str, context: Optional[dict] = None) -> ListeningHistory:
    context_type = context.get('type') if context else None
    context_uri = context.get('uri') if context else None
    listening_history_data = {
        'track_id': track_id,
        'context_type': context_type,
        'context_uri': context_uri,
        'record_type': record_type,
        'played_at': played_at
    }

    listening_history = ListeningHistory.create_record(listening_history_data)
    logger.info(f"Created listening history for track {track_id} at {played_at}")

    return listening_history