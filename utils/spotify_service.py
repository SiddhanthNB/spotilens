import requests
import base64
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

    def _get_access_token(self) -> str:
        """
        Generate access token using client credentials and refresh token
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

        try:
            response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
            response.raise_for_status()
            access_token = response.json()["access_token"]
            logger.info("Successfully generated new access token")
            return access_token
        except Exception as e:
            logger.error(f"Error generating access token: {e}")
            raise Exception(f"Failed to generate access token: {e}")

    def _ensure_valid_token(self) -> None:
        if not self.access_token:
            self.access_token = self._get_access_token()

    def fetch_recently_played(self, limit: int = 50) -> Optional[Dict[str, Any]]:
        """
        Fetch recently played tracks from Spotify API
        """
        url = f"{self.base_url}/me/player/recently-played"
        params = {"limit": limit}

        try:
            self._ensure_valid_token()
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            logger.info(f"Successfully fetched {limit} recently played tracks")
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching recently played tracks: {e}")
            return None

    def fetch_artists(self):
        pass

    def fetch_albums(self):
        pass
