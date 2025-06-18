import requests
import base64
import time
from datetime import datetime
from config.logger import logger
import utils.constants as constants
from typing import Dict, Optional, Any

class SpotifyService:
    def __init__(self):
        self.access_token = None
        self.client_id = constants.SPOTIFY_CLIENT_ID
        self.client_secret = constants.SPOTIFY_CLIENT_SECRET
        self.refresh_token = constants.SPOTIFY_REFRESH_TOKEN
        self.base_url = "https://api.spotify.com/v1"

    def _get_access_token(self, max_retries: int = 5) -> str:
        """
        Generate access token using client credentials and refresh token with retry logic
        """
        auth_str = f"{self.client_id}:{self.client_secret}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()
        headers = {
            "Authorization": f"Basic {b64_auth_str}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "https://accounts.spotify.com/api/token",
                    headers=headers,
                    data=data,
                    timeout=10
                )
                response.raise_for_status()
                access_token = response.json()["access_token"]
                logger.info("Successfully generated new access token")
                return access_token
            except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to get access token after {max_retries} attempts: {str(e)}")
                    raise

                wait_time = (2 ** attempt) + (0.1 * attempt)
                logger.warning(f"Access token request failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time:.1f}s: {str(e)}")
                time.sleep(wait_time)

    def _ensure_valid_token(self) -> None:
        if not self.access_token:
            self.access_token = self._get_access_token()

    def fetch_recently_played(self, limit: int = 50, cutoff_timestamp: str = '2025-06-10T00:00:00.000Z') -> Optional[Dict[str, Any]]:
        """
        Fetch recently played tracks from Spotify API
        """
        url = f"{self.base_url}/me/player/recently-played"
        cutoff_timestamp_dt = datetime.fromisoformat(cutoff_timestamp.replace('Z', '+00:00'))
        params = {"limit": limit, "after": int(cutoff_timestamp_dt.timestamp() * 1000)}

        self._ensure_valid_token()
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        logger.info(f"Successfully fetched {limit} recently played tracks")
        return response.json()

    def fetch_artists(self):
        pass

    def fetch_albums(self):
        pass
