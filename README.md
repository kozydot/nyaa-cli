# Nyaa CLI

CLI tool for searching, viewing, and downloading anime torrents from [nyaa.si](https://nyaa.si).

<p align="center">
<a href="https://github.com/kozydot/nyaa-cli"><img src="https://img.shields.io/github/license/kozydot/nyaa-cli?style=for-the-badge&color=blue" alt="License"></a>
<a href="https://python.org"><img src="https://img.shields.io/badge/python-3.8+-blue.svg?style=for-the-badge" alt="Python"></a>
</p>

## Features

✨ **Easy to Use**: Simple CLI interface with intuitive commands  
📥 **Direct Downloads**: Downloads torrent files directly to your machine  
🔍 **Smart Search**: Filter by subcategory, sort by various criteria  
🔗 **URL Support**: View and download torrents directly from Nyaa.si URLs  
📊 **Progress Tracking**: Real-time download progress with speed and ETA  
📝 **Rich Output**: Clean, formatted search results  
🔄 **Pagination**: Navigate through large result sets  
👤 **User Search**: Find torrents from specific uploaders  
💡 **Detailed Help**: Comprehensive built-in help system

## How it works

This CLI **scrapes the public HTML pages of [nyaa.si](https://nyaa.si)** to perform searches, retrieve torrent metadata, and download `.torrent` files.  
It does **not** rely on any third-party API or proxy service.

## Installation

```bash
# Clone the repository
git clone https://github.com/kozydot/nyaa-cli
cd nyaa-cli

# Install the package
pip install .
```

## Quick Start

```bash
# View detailed help
nyaa help

# Search for torrents (defaults to English-translated anime)
nyaa search "anime name"

# View torrent from Nyaa.si URL
nyaa view "https://nyaa.si/view/1234567"

# Download:
# 1. Press 'd'
# 2. Enter the number of your choice
# 3. File downloads automatically to downloads/
```

## Usage

### Help Command

```bash
# Show comprehensive help
nyaa help

# During search/user results, press 'h' for help
```

### Search Commands

```bash
# Basic search (defaults to English-translated anime)
nyaa search "anime name"

# Search with specific subcategory
nyaa search "anime name" --subcategory "eng"

# Sort results
nyaa search "anime name" --sort seeders --order desc

# Adjust page size
nyaa search "anime name" --page-size 15
```

### User Search

```bash
# Search by uploader (defaults to English-translated anime)
nyaa user "username"

# Search user with query and subcategory
nyaa user "username" --query "anime name" --subcategory "eng"
```

### View Torrent

```bash
# View torrent using Nyaa.si URL
nyaa view "https://nyaa.si/view/1234567"

# View torrent using just the ID
nyaa view 1234567
```

The view command shows detailed information about the torrent and offers to download it directly.

### Navigation

While viewing results:
- `n` - Next page
- `p` - Previous page
- `d` - Download selected torrent
- `h` - Show help
- `q` - Quit

## Subcategories

Available anime subcategories:
- eng (English-translated, default)
- non-eng (Non-English)
- raw (Raw)
- amv (Anime Music Video)

## File Management

Downloads are automatically saved to `downloads/` in your working directory:
- Automatically creates directory if needed
- Sanitizes filenames for compatibility
- Shows download progress with:
  - Transfer speed
  - File size
  - Time remaining
- Clear success/failure messages

## Error Handling

Handles errors gracefully, including:
- Network issues
- Invalid URLs or IDs
- Invalid search terms
- Download failures
- File system errors

## Requirements

- Python 3.8+
- requests
- beautifulsoup4
- rich
- typer
- pytest (for development)

## Development

```bash
# Install in development mode
pip install -e .

# Run tests
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is **unofficial** and **not affiliated** with Nyaa.si.  
It relies on scraping and may break if the site changes.  
Use responsibly and in accordance with your local laws and regulations.

## Author

[@kozydot](https://github.com/kozydot)
