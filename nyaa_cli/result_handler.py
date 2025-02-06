"""
Result handler module for processing and displaying search results.
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

@dataclass
class TorrentResult:
    """Data class for storing torrent information."""
    title: str
    download_link: str
    size: str
    seeders: int
    leechers: int
    downloads: int
    category: str
    date: str

class ResultHandler:
    """Handles processing and display of search results."""
    
    def __init__(self):
        """Initialize the result handler."""
        self.console = Console()
        self._current_page = 1
        self._results_cache = {}
        self._last_query = None
        self._current_page_results: List[TorrentResult] = []
        
    def process_results(self, api_response: Dict) -> List[TorrentResult]:
        """
        Process API response into TorrentResult objects.
        
        Args:
            api_response: Raw API response dictionary
            
        Returns:
            List of TorrentResult objects
        """
        results = []
        for item in api_response.get("data", []):
            result = TorrentResult(
                title=item.get("title", "Unknown"),
                download_link=item.get("torrent", ""),
                size=item.get("size", "Unknown"),
                seeders=int(item.get("seeders", "0")),
                leechers=int(item.get("leechers", "0")),
                downloads=int(item.get("completed", "0")),
                category=item.get("category", "Unknown"),
                date=item.get("date", "Unknown")
            )
            results.append(result)
        return results
    
    def display_results(self, results: List[TorrentResult], page_size: int = 10) -> List[TorrentResult]:
        """
        Display results in a formatted table.
        
        Args:
            results: List of TorrentResult objects
            page_size: Number of results per page
            
        Returns:
            List of TorrentResult objects displayed on the current page
        """
        if not results:
            self.console.print("[yellow]No results found.[/yellow]")
            return []
            
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Title", width=50, no_wrap=False)
        table.add_column("Size", justify="right")
        table.add_column("S", justify="right")
        table.add_column("L", justify="right")
        table.add_column("Downloads", justify="right")
        table.add_column("Date")
        
        start_idx = (self._current_page - 1) * page_size
        end_idx = start_idx + page_size
        page_results = results[start_idx:end_idx]
        self._current_page_results = page_results
        
        for idx, result in enumerate(page_results, 1):
            title = result.title
            if len(title) > 47:
                title = title[:47] + "..."
                
            table.add_row(
                str(idx),
                title,
                result.size,
                str(result.seeders),
                str(result.leechers),
                str(result.downloads),
                result.date
            )
        
        self.console.print(table)
        self._display_pagination_info(len(results), page_size)
        return page_results
    
    def _display_pagination_info(self, total_results: int, page_size: int):
        """Display pagination information."""
        total_pages = (total_results + page_size - 1) // page_size
        self.console.print(
            f"\nPage {self._current_page} of {total_pages} "
            f"(Total results: {total_results})",
            style="dim"
        )
    
    def get_download_link(self, selection: int) -> Optional[Tuple[str, str]]:
        """
        Get the download link for a selected result.
        
        Args:
            selection: The selected result number (1-based)
            
        Returns:
            Tuple of (title, download_link) if valid selection, None otherwise
        """
        if 1 <= selection <= len(self._current_page_results):
            result = self._current_page_results[selection - 1]
            return result.title, result.download_link
        return None
        
    def cache_results(self, query: str, results: List[TorrentResult]):
        """
        Cache results for a query.
        
        Args:
            query: Search query
            results: List of TorrentResult objects
        """
        self._results_cache[query] = results
        self._last_query = query
    
    def get_cached_results(self, query: str) -> Optional[List[TorrentResult]]:
        """
        Get cached results for a query.
        
        Args:
            query: Search query
            
        Returns:
            Cached results if available, None otherwise
        """
        return self._results_cache.get(query)
    
    def next_page(self):
        """Move to next page of results."""
        self._current_page += 1
        
    def previous_page(self):
        """Move to previous page of results."""
        if self._current_page > 1:
            self._current_page -= 1
            
    def reset_pagination(self):
        """Reset pagination to first page."""
        self._current_page = 1