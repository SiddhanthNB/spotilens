from invoke.tasks import task
from config.logger import logger
from db.models.sync_logs import SyncLog
from utils.spotify_service import SpotifyService
from utils.helper import store_spotify_track_in_db

@task()
def sync_data_with_spotify():
    spotify_service = SpotifyService()

    _sync_recently_played(spotify_service)
    _sync_artists(spotify_service)
    _sync_albums(spotify_service)

    logger.info('Syncing completed.')

# helper functions
def _sync_recently_played(spotify_service):
    log_payload = {
        'status': None,
        'sync_source': 'recently-played-api',
        'response': None
    }
    try:
        response = spotify_service.fetch_recently_played()
        [ store_spotify_track_in_db(item, 'daily-sync') for item in response['items'] ]
        log_payload['status'] = True
    except Exception as e:
        logger.error(f'Could not sync with spotify: {str(e)}')
        log_payload['response'] = str(e)
        log_payload['status'] = False
    finally:
        SyncLog.create_record(log_payload)

def _sync_artists(spotify_service):
    pass

def _sync_albums(spotify_service):
    pass
