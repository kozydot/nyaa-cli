"""
CLI interface module for the Nyaa.si torrent search application.
"""
from typing import Optional
import typer
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel

from .api import NyaaAPI, NyaaAPIError
from .result_handler import ResultHandler
from .download_handler import DownloadHandler

app = typer.Typer(help="Nyaa.si CLI - Search for anime torrents")
console = Console()
api_client = NyaaAPI()
result_handler = ResultHandler()
download_handler = DownloadHandler()

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

@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    category: str = typer.Option("anime", help="Torrent category"),
    subcategory: Optional[str] = typer.Option(None, help="Torrent subcategory"),
    sort: Optional[str] = typer.Option(
        None,
        help="Sort results by: id, seeders, leechers, size, downloads"
    ),
    order: str = typer.Option("desc", help="Sort order: asc or desc"),
    page_size: int = typer.Option(10, help="Results per page")
):
    """
    Search for anime torrents on Nyaa.si
    """
    try:
        with console.status("[bold green]Searching for torrents..."):
            response = api_client.search_anime(
                query=query,
                category=category,
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
                choices=["n", "p", "d", "q"],
                default="q",
                show_choices=False,
                show_default=False
            )
            
            if command == "q":
                break
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
    query: Optional[str] = typer.Option(None, help="Optional search query"),
    category: Optional[str] = typer.Option(None, help="Optional category filter"),
    page_size: int = typer.Option(10, help="Results per page")
):
    """
    Search for torrents by username
    """
    try:
        with console.status(f"[bold green]Searching for torrents by {username}..."):
            response = api_client.search_by_user(
                username=username,
                query=query,
                category=category
            )
            
        results = result_handler.process_results(response)
        result_handler.cache_results(f"user:{username}", results)
        result_handler.reset_pagination()
        result_handler.display_results(results, page_size)
        
        while True:
            show_navigation_help()
            command = Prompt.ask(
                "\nEnter command",
                choices=["n", "p", "d", "q"],
                default="q",
                show_choices=False,
                show_default=False
            )
            
            if command == "q":
                break
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
def torrent(
    torrent_id: str = typer.Argument(..., help="Torrent ID")
):
    """
    Get details for a specific torrent by ID
    """
    try:
        with console.status("[bold green]Fetching torrent details..."):
            response = api_client.get_torrent_by_id(torrent_id)
            
        if "data" in response:
            data = response["data"]
            console.print("\n[bold]Torrent Details:[/bold]")
            console.print(f"Title: {data.get('title', 'Unknown')}")
            console.print(f"Category: {data.get('category', 'Unknown')}")
            console.print(f"Size: {data.get('size', 'Unknown')}")
            console.print(f"Date: {data.get('date', 'Unknown')}")
            console.print(f"Seeders: {data.get('seeders', 0)}")
            console.print(f"Leechers: {data.get('leechers', 0)}")
            console.print(f"Downloads: {data.get('completed', 0)}")
            
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

def run():
    """Entry point for the CLI application."""
    app()