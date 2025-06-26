import json
from invoke.tasks import task
from config.logger import logger
from config.postgres import db_session, close_session
from utils.helper import store_spotify_track_in_db
from sqlalchemy import text

@task()
def create_tables_in_db(ctx):
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
def populate_db_with_historical_listening_data(ctx):
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
    close_session()

@task()
def populate_track_names_bulk(ctx):
    try:
        # Raw SQL query to update track_name from tracks table
        # CORRECTED: Proper explicit JOIN syntax for PostgreSQL UPDATE
        update_query = """
            UPDATE spotilens__listening_history
            SET track_name = t.name, updated_at = NOW()
            FROM spotilens__tracks t
            WHERE spotilens__listening_history.track_id = t.track_id
            AND spotilens__listening_history.track_name IS NULL
        """

        result = db_session.execute(text(update_query))
        db_session.commit()

        rows_updated = result.rowcount
        logger.info(f"Bulk update completed. Updated {rows_updated} records with track names")

        return True

    except Exception as e:
        logger.error(f"Error in populate_track_names_bulk: {e}", exc_info=True)
        db_session.rollback()
        return False
    finally:
        db_session.close()
