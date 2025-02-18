"""
API client module for interacting with the nyaa.si API.
"""
from typing import Dict, List, Optional, Union
import logging
import requests
from requests.exceptions import RequestException

class NyaaAPIError(Exception):
    """Base exception for Nyaa API errors."""
    pass

class NyaaAPI:
    """Client for interacting with the nyaa.si API."""
    
    BASE_URL = "https://nyaaapi.onrender.com"
    SUBCATEGORY_ANIME_ENG = "eng"  # API uses "eng" instead of "English-translated"
    
    # API Categories
    CATEGORIES = {
        "anime": "anime",
        "manga": "manga",
        "audio": "audio",
        "pictures": "pictures",
        "live_action": "live_action",
        "software": "software"
    }
    
    # API Subcategories
    SUBCATEGORIES = {
        "anime": ["amv", "eng", "non-eng", "raw"],
        "manga": ["eng", "non-eng", "raw"],
        "audio": ["lossy", "lossless"],
        "pictures": ["photos", "graphics"],
        "live_action": ["promo", "eng", "non-eng", "raw"],
        "software": ["application", "games"]
    }
    
    def __init__(self, debug: bool = False):
        """
        Initialize the API client.
        
        Args:
            debug: Enable debug logging
        """
        self.session = requests.Session()
        self.debug = debug
        self.logger = logging.getLogger(__name__)
        if debug:
            logging.basicConfig(level=logging.DEBUG)
    
    def _make_request(self, endpoint: str) -> Dict:
        """
        Make a request to the API.
        
        Args:
            endpoint: API endpoint path with query parameters
            
        Returns:
            Dict containing the API response
            
        Raises:
            NyaaAPIError: If the request fails
        """
        try:
            # First check if API is available
            try:
                health_check = self.session.get(self.BASE_URL)
                health_check.raise_for_status()
            except RequestException:
                raise NyaaAPIError("The Nyaa API service is currently unavailable. Please try again later.")

            # Make the actual request
            url = f"{self.BASE_URL}/{endpoint}"
            
            if self.debug:
                self.logger.debug(f"Making request to: {url}")
            
            response = self.session.get(url, timeout=10)  # Add timeout
            response.raise_for_status()
            
            try:
                data = response.json()
                if not data:  # If response is empty
                    return {"data": [], "message": "No results found"}
                return data
            except ValueError as e:
                raise NyaaAPIError("Failed to parse API response") from e
                
        except RequestException as e:
            if "404" in str(e):
                raise NyaaAPIError("No results found for your search query") from e
            raise NyaaAPIError(f"API request failed: {str(e)}") from e
    
    def search_anime(
        self,
        query: str,
        category: str = "anime",
        subcategory: Optional[str] = SUBCATEGORY_ANIME_ENG,
        sort: Optional[str] = None,
        order: str = "desc"
    ) -> Dict:
        """
        Search for anime torrents.
        
        Args:
            query: Search query string
            category: Torrent category (default: "anime")
            subcategory: Subcategory (default: "eng")
            sort: Sort field (id, seeders, leechers, size, downloads)
            order: Sort order (asc, desc)
            
        Returns:
            Dict containing search results
        """
        from urllib.parse import urlencode

        # Start with just the basic search parameters
        query_params = {
            "q": query
        }

        # Build the endpoint according to API docs
        endpoint = f"nyaa?{urlencode(query_params)}"
        return self._make_request(endpoint)
    
    def get_torrent_by_id(self, torrent_id: Union[str, int]) -> Dict:
        """
        Get torrent details by ID.
        
        Args:
            torrent_id: Torrent ID
            
        Returns:
            Dict containing torrent details
        """
        endpoint = f"nyaa/id/{torrent_id}"
        return self._make_request(endpoint)
    
    def search_by_user(
        self,
        username: str,
        query: Optional[str] = None,
        category: str = "anime",
        subcategory: Optional[str] = SUBCATEGORY_ANIME_ENG
    ) -> Dict:
        """
        Search torrents by username.
        
        Args:
            username: Username to search for
            query: Optional search query
            category: Optional category (default: "anime")
            subcategory: Optional subcategory (default: "eng")
            
        Returns:
            Dict containing search results
        """
        # Build endpoint according to API docs
        base_endpoint = f"nyaa/user/{username}"

        # Add query parameter if provided
        if query:
            endpoint = f"{base_endpoint}?q={query}"
        else:
            endpoint = base_endpoint

        # Add category if it's anime and has subcategory
        if category == "anime" and subcategory:
            endpoint += f"&category={subcategory}" if "?" in endpoint else f"?category={subcategory}"

        return self._make_request(endpoint)