"""
Download handler module for managing torrent downloads.
"""
import os
from pathlib import Path
from typing import Optional
import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

class DownloadHandler:
    """Handles downloading and saving torrent files."""
    
    def __init__(self):
        """Initialize the download handler."""
        self.console = Console()
        self.downloads_dir = Path("downloads")
        self._ensure_download_directory()
        
    def _ensure_download_directory(self):
        """Create downloads directory if it doesn't exist."""
        self.downloads_dir.mkdir(exist_ok=True)
        
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize the filename to be safe for all operating systems.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Replace invalid characters with underscore
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def download_torrent(self, url: str, title: str) -> Optional[Path]:
        """
        Download a torrent file to the downloads directory.
        
        Args:
            url: Torrent file URL
            title: Title of the torrent (used for filename)
            
        Returns:
            Path to the downloaded file if successful, None otherwise
        """
        try:
            # Create a sanitized filename
            filename = self._sanitize_filename(title)
            if not filename.endswith('.torrent'):
                filename += '.torrent'
            
            filepath = self.downloads_dir / filename
            
            # Download with progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
                console=self.console
            ) as progress:
                
                download_task = progress.add_task(
                    f"Downloading: {filename}", 
                    total=None
                )
                
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                # Get content length if available
                total_size = int(response.headers.get('content-length', 0))
                if total_size:
                    progress.update(download_task, total=total_size)
                
                # Download the file
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress.update(download_task, advance=len(chunk))
                
            self.console.print(f"\n[green]Successfully downloaded to:[/green] {filepath}")
            return filepath
            
        except requests.RequestException as e:
            self.console.print(f"[red]Error downloading torrent:[/red] {str(e)}")
            return None
        except IOError as e:
            self.console.print(f"[red]Error saving torrent file:[/red] {str(e)}")
            return None