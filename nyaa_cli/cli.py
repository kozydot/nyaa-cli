"""
CLI interface module for the Nyaa.si torrent search application.
"""
from typing import Optional
import re
import typer
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from .api import NyaaAPI, NyaaAPIError
from .result_handler import ResultHandler
from .download_handler import DownloadHandler

app = typer.Typer(help="Nyaa.si CLI - Search for anime torrents")
console = Console()
api_client = NyaaAPI(debug=False)
result_handler = ResultHandler()
download_handler = DownloadHandler()

HELP_TEXT = """
# Nyaa.si CLI Help

A command-line interface for searching and downloading anime torrents from Nyaa.si.

## Commands

### Search
Search for anime torrents:
```bash
nyaa search "your query"
```

Options:
- `-s, --subcategory`: Filter by subcategory (default: English-translated)
  - Available: English-translated, Non-English-translated, Raw
- `-S, --sort`: Sort results by field
  - Available: id, seeders, leechers, size, downloads
- `-o, --order`: Sort order (asc/desc)
- `-p, --page-size`: Number of results per page

Example:
```bash
nyaa search "one piece" -s "English-translated" -S seeders -o desc
```

### User Search
Search torrents by username:
```bash
nyaa user "username"
```

Options:
- `-q, --query`: Optional search term
- `-s, --subcategory`: Filter by subcategory
- `-p, --page-size`: Number of results per page

Example:
```bash
nyaa user "SubsPlease" -q "one piece" -s "English-translated"
```

### View Torrent
Get details for a specific torrent using URL or ID:
```bash
# Using URL
nyaa view "https://nyaa.si/view/1931737"

# Using ID
nyaa view 1931737
```

### Torrent Info (deprecated, use view instead)
Get detailed information about a specific torrent:
```bash
nyaa torrent "torrent_id"
```

## Navigation Commands

When viewing search results:
- `n`: Next page
- `p`: Previous page
- `d`: Download (you'll be prompted for the number)
- `q`: Quit/Exit to command prompt

## Download Location

Downloads are saved to the `downloads/` directory in your current working directory.

## Examples

1. Search for recent English anime:
```bash
nyaa search "latest" -s "English-translated" -S "id" -o "desc"
```

2. Search for high-seeded torrents:
```bash
nyaa search "anime" -S "seeders" -o "desc"
```

3. View torrent details by URL:
```bash
nyaa view "https://nyaa.si/view/1931737"
```
"""

SUBCATEGORY_CHOICES = [
    "English-translated",
    "Non-English-translated",
    "Raw"
]

def show_navigation_help():
    """Display navigation help panel."""
    help_text = (
        "Navigation Commands:\n"
        "  [bold]n[/bold] - Next page\n"
        "  [bold]p[/bold] - Previous page\n"
        "  [bold]d[/bold] - Download (you'll be prompted for the number)\n"
        "  [bold]q[/bold] - Quit/Exit to command prompt\n\n"
        "To download a torrent, enter [bold]d[/bold] and then select the number from the first column\n"
        "Downloads are saved to the [bold]downloads/[/bold] directory"
    )
    console.print(Panel(help_text, title="Available Commands"))

def handle_download_selection(results):
    """Handle the download selection process."""
    try:
        selection = IntPrompt.ask(
            "\nEnter the number of the torrent to download (1-10)",
            default=1
        )
        result = result_handler.get_download_link(selection)
        if result:
            title, download_link = result
            console.print(f"\nSelected: [cyan]{title}[/cyan]")
            download_handler.download_torrent(download_link, title)
        else:
            console.print("[red]Invalid selection. Please choose a number from the list.[/red]")
    except (ValueError, TypeError):
        console.print("[red]Invalid input. Please enter a valid number.[/red]")

def extract_torrent_id(url_or_id: str) -> str:
    """
    Extract torrent ID from URL or return the ID if it's just a number.
    
    Args:
        url_or_id: Nyaa.si URL or torrent ID
        
    Returns:
        Torrent ID as string
        
    Raises:
        ValueError: If the URL or ID format is invalid
    """
    # If it's a URL, extract the ID
    url_match = re.match(r'^https?://nyaa\.si/view/(\d+)/?$', url_or_id)
    if url_match:
        return url_match.group(1)
    
    # If it's just a number, return it
    if url_or_id.isdigit():
        return url_or_id
        
    raise ValueError(
        "Invalid format. Please provide either a Nyaa.si URL (https://nyaa.si/view/ID) or just the ID number"
    )

def display_torrent_info(data: dict) -> None:
    """Display torrent information in a formatted way."""
    console.print("\n[bold]Torrent Details:[/bold]")
    console.print(f"Title: {data.get('title', 'Unknown')}")
    console.print(f"Category: {data.get('category', 'Unknown')}")
    console.print(f"Size: {data.get('size', 'Unknown')}")
    console.print(f"Date: {data.get('time', 'Unknown')}")
    console.print(f"Seeders: {data.get('seeders', 0)}")
    console.print(f"Leechers: {data.get('leechers', 0)}")
    console.print(f"Downloads: {data.get('completed', 0)}")

@app.command()
def help():
    """Show detailed help information."""
    console.print(Markdown(HELP_TEXT))

@app.command()
def view(
    url_or_id: str = typer.Argument(
        ...,
        help="Nyaa.si URL (https://nyaa.si/view/ID) or torrent ID"
    )
):
    """
    View details for a specific torrent using URL or ID
    """
    try:
        torrent_id = extract_torrent_id(url_or_id)
        
        with console.status("[bold green]Fetching torrent details..."):
            response = api_client.get_torrent_by_id(torrent_id)
            
        if "data" in response:
            data = response["data"]
            display_torrent_info(data)
            
            download_link = data.get('torrent')
            if download_link:
                if Prompt.ask(
                    "\nWould you like to download this torrent?",
                    choices=["y", "n"],
                    default="n"
                ) == "y":
                    download_handler.download_torrent(
                        download_link,
                        data.get('title', 'Unknown')
                    )
            else:
                console.print("\n[yellow]Download link not available.[/yellow]")
        else:
            console.print("[yellow]No torrent found with that ID.[/yellow]")
            
    except ValueError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
    except NyaaAPIError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
    except Exception as e:
        console.print(f"[red]An unexpected error occurred:[/red] {str(e)}")

@app.command(deprecated=True)
def torrent(
    torrent_id: str = typer.Argument(..., help="Torrent ID")
):
    """
    Get details for a specific torrent by ID (deprecated, use view instead)
    """
    try:
        with console.status("[bold green]Fetching torrent details..."):
            response = api_client.get_torrent_by_id(torrent_id)
            
        if "data" in response:
            data = response["data"]
            display_torrent_info(data)
            
            download_link = data.get('torrent')
            if download_link:
                if Prompt.ask(
                    "\nWould you like to download this torrent?",
                    choices=["y", "n"],
                    default="n"
                ) == "y":
                    download_handler.download_torrent(
                        download_link,
                        data.get('title', 'Unknown')
                    )
            else:
                console.print("\n[yellow]Download link not available.[/yellow]")
        else:
            console.print("[yellow]No torrent found with that ID.[/yellow]")
            
    except NyaaAPIError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
    except Exception as e:
        console.print(f"[red]An unexpected error occurred:[/red] {str(e)}")

@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    subcategory: str = typer.Option(
        api_client.SUBCATEGORY_ANIME_ENG,
        "--subcategory",
        "-s",
        help="Anime subcategory",
        show_choices=True,
        case_sensitive=False
    ),
    sort: Optional[str] = typer.Option(
        None,
        "--sort",
        "-S",
        help="Sort results by: id, seeders, leechers, size, downloads"
    ),
    order: str = typer.Option(
        "desc",
        "--order",
        "-o",
        help="Sort order: asc or desc"
    ),
    page_size: int = typer.Option(
        10,
        "--page-size",
        "-p",
        help="Results per page"
    )
):
    """
    Search for anime torrents on Nyaa.si
    """
    try:
        with console.status("[bold green]Searching for torrents..."):
            response = api_client.search_anime(
                query=query,
                subcategory=subcategory,
                sort=sort,
                order=order
            )
            
        results = result_handler.process_results(response)
        result_handler.cache_results(query, results)
        result_handler.reset_pagination()
        result_handler.display_results(results, page_size)
        
        while True:
            show_navigation_help()
            command = Prompt.ask(
                "\nEnter command",
                choices=["n", "p", "d", "q", "h"],
                default="q",
                show_choices=False,
                show_default=False
            )
            
            if command == "q":
                break
            elif command == "h":
                help()
            elif command == "n":
                result_handler.next_page()
                console.clear()
                result_handler.display_results(results, page_size)
            elif command == "p":
                result_handler.previous_page()
                console.clear()
                result_handler.display_results(results, page_size)
            elif command == "d":
                handle_download_selection(results)
                
    except NyaaAPIError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
    except Exception as e:
        console.print(f"[red]An unexpected error occurred:[/red] {str(e)}")

@app.command()
def user(
    username: str = typer.Argument(..., help="Username to search for"),
    query: Optional[str] = typer.Option(
        None,
        "--query",
        "-q",
        help="Optional search query"
    ),
    subcategory: str = typer.Option(
        api_client.SUBCATEGORY_ANIME_ENG,
        "--subcategory",
        "-s",
        help="Anime subcategory",
        show_choices=True,
        case_sensitive=False
    ),
    page_size: int = typer.Option(
        10,
        "--page-size",
        "-p",
        help="Results per page"
    )
):
    """
    Search for torrents by username
    """
    try:
        with console.status(f"[bold green]Searching for torrents by {username}..."):
            response = api_client.search_by_user(
                username=username,
                query=query,
                subcategory=subcategory
            )
            
        results = result_handler.process_results(response)
        result_handler.cache_results(f"user:{username}", results)
        result_handler.reset_pagination()
        result_handler.display_results(results, page_size)
        
        while True:
            show_navigation_help()
            command = Prompt.ask(
                "\nEnter command",
                choices=["n", "p", "d", "q", "h"],
                default="q",
                show_choices=False,
                show_default=False
            )
            
            if command == "q":
                break
            elif command == "h":
                help()
            elif command == "n":
                result_handler.next_page()
                console.clear()
                result_handler.display_results(results, page_size)
            elif command == "p":
                result_handler.previous_page()
                console.clear()
                result_handler.display_results(results, page_size)
            elif command == "d":
                handle_download_selection(results)
                
    except NyaaAPIError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
    except Exception as e:
        console.print(f"[red]An unexpected error occurred:[/red] {str(e)}")

def run():
    """Entry point for the CLI application."""
    app()
