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
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the API.
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            
        Returns:
            Dict containing the API response
            
        Raises:
            NyaaAPIError: If the request fails
        """
        try:
            url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
            if self.debug:
                self.logger.debug(f"Making request to: {url} with params: {params}")
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if self.debug and "data" in data:
                for item in data["data"]:
                    self.logger.debug(f"Received date: {item.get('date', 'No date')}")
                    
            return data
        except RequestException as e:
            raise NyaaAPIError(f"API request failed: {str(e)}") from e
        except ValueError as e:
            raise NyaaAPIError("Failed to parse API response") from e
    
    def search_anime(
        self,
        query: str,
        category: str = "anime",
        subcategory: Optional[str] = None,
        page: int = 1,
        sort: Optional[str] = None,
        order: str = "desc"
    ) -> Dict:
        """
        Search for anime torrents.
        
        Args:
            query: Search query string
            category: Torrent category (default: "anime")
            subcategory: Optional subcategory
            page: Page number (default: 1)
            sort: Sort field (id, seeders, leechers, size, downloads)
            order: Sort order (asc, desc)
            
        Returns:
            Dict containing search results
        """
        params = {
            "q": query,
            "category": category,
            "p": page,
        }
        
        if subcategory:
            params["subcategory"] = subcategory
        if sort:
            params["sort"] = sort
        if order:
            params["order"] = order
            
        response = self._make_request("nyaa", params)
        
        # Parse and standardize dates in the response
        if "data" in response:
            for item in response["data"]:
                if "date" in item:
                    if self.debug:
                        self.logger.debug(f"Processing date: {item['date']}")
                    # Keep the date as is, will be formatted by ResultHandler
                    continue
                    
        return response
    
    def get_torrent_by_id(self, torrent_id: Union[str, int]) -> Dict:
        """
        Get torrent details by ID.
        
        Args:
            torrent_id: Torrent ID
            
        Returns:
            Dict containing torrent details
        """
        return self._make_request(f"nyaa/id/{torrent_id}")
    
    def search_by_user(
        self,
        username: str,
        query: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict:
        """
        Search torrents by username.
        
        Args:
            username: Username to search for
            query: Optional search query
            category: Optional category filter
            
        Returns:
            Dict containing search results
        """
        params = {}
        if query:
            params["q"] = query
        if category:
            params["category"] = category
            
        return self._make_request(f"nyaa/user/{username}", params)