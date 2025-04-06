"""
Unofficial API client for scraping nyaa.si directly.
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, Union
import logging

class NyaaAPIError(Exception):
    """Base exception for Nyaa API errors."""
    pass

class NyaaAPI:
    """Client for scraping nyaa.si website."""
    
    BASE_URL = "https://nyaa.si"
    SUBCATEGORY_ANIME_ENG = "eng"  # default subcategory
    
    # Category codes for URL parameter 'c'
    # Format: <main_category>_<sub_category>
    # 0_0 = all categories
    # 1_2 = Anime - English-translated
    # 1_3 = Anime - Non-English
    # 1_4 = Anime - Raw
    CATEGORY_CODES = {
        "all": "0_0",
        "anime_eng": "1_2",
        "anime_non_eng": "1_3",
        "anime_raw": "1_4",
        "anime_amv": "1_1",
    }
    
    def __init__(self, debug: bool = False):
        self.session = requests.Session()
        self.debug = debug
        self.logger = logging.getLogger(__name__)
        if debug:
            logging.basicConfig(level=logging.DEBUG)
    
    def _log(self, message: str):
        if self.debug:
            self.logger.debug(message)
    
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
        """
        try:
            # Determine category code
            cat_code = "0_0"  # default all
            if category == "anime":
                if subcategory == "eng":
                    cat_code = self.CATEGORY_CODES["anime_eng"]
                elif subcategory == "non-eng":
                    cat_code = self.CATEGORY_CODES["anime_non_eng"]
                elif subcategory == "raw":
                    cat_code = self.CATEGORY_CODES["anime_raw"]
                elif subcategory == "amv":
                    cat_code = self.CATEGORY_CODES["anime_amv"]
                else:
                    cat_code = "1_0"  # all anime
            
            params = {
                "q": query,
                "c": cat_code,
                "f": "0"  # no filter
            }
            url = f"{self.BASE_URL}/"
            self._log(f"Search URL: {url} with params {params}")
            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            table = soup.find("table", class_="torrent-list")
            if not table:
                return {"data": [], "message": "No results found"}
            results = []
            for row in table.find("tbody").find_all("tr"):
                cols = row.find_all("td")
                title_tag = cols[1].find("a")
                title = title_tag.text.strip()
                link = title_tag.get("href", "")
                torrent_id = None
                if link:
                    import re
                    m = re.search(r'/view/(\d+)', link)
                    if m:
                        torrent_id = m.group(1)
                size = cols[3].text.strip()
                seeders = cols[5].text.strip()
                leechers = cols[6].text.strip()
                completed = cols[7].text.strip()
                category_name = cols[0].text.strip()
                date = cols[4].text.strip()
                download_url = f"{self.BASE_URL}/download/{torrent_id}.torrent" if torrent_id else None
                results.append({
                    "id": torrent_id,
                    "title": title,
                    "category": category_name,
                    "size": size,
                    "time": date,
                    "seeders": int(seeders),
                    "leechers": int(leechers),
                    "completed": int(completed),
                    "torrent": download_url
                })
            return {"data": results}
        except Exception as e:
            raise NyaaAPIError(f"Search failed: {str(e)}") from e
    
    def get_torrent_by_id(self, torrent_id: Union[str, int]) -> Dict:
        """
        Get torrent details by ID.
        """
        try:
            url = f"{self.BASE_URL}/view/{torrent_id}"
            self._log(f"Fetching torrent page: {url}")
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            title = soup.find("h3", class_="panel-title").text.strip()
            description = soup.find("div", class_="panel-body").text.strip()
            download_url = f"{self.BASE_URL}/download/{torrent_id}.torrent"
            
            # Initialize defaults
            category = "Unknown"
            size = "Unknown"
            date = "Unknown"
            seeders = 0
            leechers = 0
            downloads = 0
            
            # Parse metadata table
            info_panel = soup.find("div", class_="panel")
            if info_panel:
                rows = info_panel.find_all("tr")
                for row in rows:
                    th = row.find("td", class_="text-center")
                    if not th:
                        continue
                    label = th.text.strip().lower()
                    value_td = th.find_next_sibling("td")
                    value = value_td.text.strip() if value_td else ""
                    if "category" in label:
                        category = value
                    elif "size" in label:
                        size = value
                    elif "date" in label:
                        date = value
                    elif "seeders" in label:
                        try:
                            seeders = int(value)
                        except:
                            seeders = 0
                    elif "leechers" in label:
                        try:
                            leechers = int(value)
                        except:
                            leechers = 0
                    elif "downloads" in label:
                        try:
                            downloads = int(value)
                        except:
                            downloads = 0
            
            data = {
                "id": str(torrent_id),
                "title": title,
                "description": description,
                "torrent": download_url,
                "category": category,
                "size": size,
                "time": date,
                "seeders": seeders,
                "leechers": leechers,
                "completed": downloads
            }
            return {"data": data}
        except Exception as e:
            raise NyaaAPIError(f"Failed to fetch torrent info: {str(e)}") from e
    
    def search_by_user(
        self,
        username: str,
        query: Optional[str] = None,
        category: str = "anime",
        subcategory: Optional[str] = SUBCATEGORY_ANIME_ENG
    ) -> Dict:
        """
        Search torrents uploaded by a specific user.
        """
        try:
            # User search is done via query param 'u'
            cat_code = "0_0"
            if category == "anime":
                if subcategory == "eng":
                    cat_code = self.CATEGORY_CODES["anime_eng"]
                elif subcategory == "non-eng":
                    cat_code = self.CATEGORY_CODES["anime_non_eng"]
                elif subcategory == "raw":
                    cat_code = self.CATEGORY_CODES["anime_raw"]
                elif subcategory == "amv":
                    cat_code = self.CATEGORY_CODES["anime_amv"]
                else:
                    cat_code = "1_0"
            params = {
                "u": username,
                "c": cat_code,
                "f": "0"
            }
            if query:
                params["q"] = query
            url = f"{self.BASE_URL}/"
            self._log(f"User search URL: {url} with params {params}")
            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            table = soup.find("table", class_="torrent-list")
            if not table:
                return {"data": [], "message": "No results found"}
            results = []
            for row in table.find("tbody").find_all("tr"):
                cols = row.find_all("td")
                title_tag = cols[1].find("a")
                title = title_tag.text.strip()
                link = title_tag.get("href", "")
                torrent_id = None
                if link:
                    import re
                    m = re.search(r'/view/(\d+)', link)
                    if m:
                        torrent_id = m.group(1)
                size = cols[3].text.strip()
                seeders = cols[5].text.strip()
                leechers = cols[6].text.strip()
                completed = cols[7].text.strip()
                category_name = cols[0].text.strip()
                date = cols[4].text.strip()
                download_url = f"{self.BASE_URL}/download/{torrent_id}.torrent" if torrent_id else None
                results.append({
                    "id": torrent_id,
                    "title": title,
                    "category": category_name,
                    "size": size,
                    "time": date,
                    "seeders": int(seeders),
                    "leechers": int(leechers),
                    "completed": int(completed),
                    "torrent": download_url
                })
            return {"data": results}
        except Exception as e:
            raise NyaaAPIError(f"User search failed: {str(e)}") from e
