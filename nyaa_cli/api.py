"""
API client module for interacting with the nyaa.si API.
"""
from typing import Dict, List, Optional, Union
import requests
from requests.exceptions import RequestException

class NyaaAPIError(Exception):
    """Base exception for Nyaa API errors."""
    pass

class NyaaAPI:
    """Client for interacting with the nyaa.si API."""
    
    BASE_URL = "https://nyaaapi.onrender.com"
    
    def __init__(self):
        """Initialize the API client."""
        self.session = requests.Session()
    
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
            response = self.session.get(
                f"{self.BASE_URL}/{endpoint.lstrip('/')}",
                params=params
            )
            response.raise_for_status()
            return response.json()
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
            
        return self._make_request("nyaa", params)
    
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