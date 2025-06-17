import os
import json
from invoke.tasks import task
from config.logger import logger
from utils.helper import store_spotify_track_in_db

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
