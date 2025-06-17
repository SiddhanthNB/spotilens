import json
from invoke.tasks import task
from config.logger import logger
from utils.helper import store_spotify_track_in_db

@task()
def create_tables_in_db():
    from db.models.albums import Album
    from db.models.artists import Artist
    from db.models.tracks import Track
    from db.models.album_artists import AlbumArtist
    from db.models.track_artists import TrackArtist
    from db.models.listening_history import ListeningHistory
    from db.models.sync_logs import SyncLog
    import utils.constants as constants
    from sqlalchemy import create_engine
    from db.models.base_model import Base

    engine = create_engine(constants.SUPABASE_DB_URL)
    Base.metadata.create_all(engine)

@task()
def populate_db_with_historical_listening_data():
    logger.setLevel('WARNING')

    with open('data/final_listening_history.json', 'r') as f:
        listening_history = json.load(f)

    listening_history_sorted = sorted(listening_history, key=lambda x: x['played_at'])

    for i, item in enumerate(listening_history_sorted, 1):
        try:
            print(f"Processing item {i}/{len(listening_history_sorted)}")
            store_spotify_track_in_db(item, 'historical-data')
        except Exception as e:
            print(f"Error processing track with id {item.get('track', {}).get('id')}: {e}")
            print('continuing...')
