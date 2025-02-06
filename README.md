# Nyaa CLI

A command-line interface for searching and downloading anime torrents from Nyaa.si using their unofficial API.

<p align="center">
<a href="https://github.com/kozydot/nyaa-cli"><img src="https://img.shields.io/github/license/kozydot/nyaa-cli?style=for-the-badge&color=blue" alt="License"></a>
<a href="https://python.org"><img src="https://img.shields.io/badge/python-3.8+-blue.svg?style=for-the-badge" alt="Python"></a>
</p>

## Features

✨ **Easy to Use**: Simple CLI interface with intuitive commands  
📥 **Direct Downloads**: Downloads torrent files directly to your machine  
🔍 **Smart Search**: Filter by category, sort by various criteria  
📊 **Progress Tracking**: Real-time download progress with speed and ETA  
📝 **Rich Output**: Clean, formatted search results  
🔄 **Pagination**: Navigate through large result sets  
👤 **User Search**: Find torrents from specific uploaders

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
# Search for torrents
nyaa search "anime name"

# Download:
# 1. Press 'd'
# 2. Enter the number of your choice
# 3. File downloads automatically to downloads/
```

## Usage

### Search Commands

```bash
# Basic search
nyaa search "anime name"

# Search with filters
nyaa search "anime name" --category anime --subcategory eng

# Sort results
nyaa search "anime name" --sort seeders --order desc

# Adjust page size
nyaa search "anime name" --page-size 15
```

### User Search

```bash
# Search by uploader
nyaa user "username"

# Search user with query
nyaa user "username" --query "anime name"
```

### Navigation

While viewing results:
- `n` - Next page
- `p` - Previous page
- `d` - Download selected torrent
- `q` - Quit

## Categories

### Main Categories
- anime
- manga
- audio
- pictures
- live_action
- software

### Anime Subcategories
- amv
- eng
- non-eng
- raw

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

Comprehensive error handling for:
- API connection issues
- Invalid search terms
- Rate limiting
- Download failures
- File system errors

## Requirements

- Python 3.8+
- requests
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

This tool uses the unofficial Nyaa.si API and is not affiliated with Nyaa.si. Use responsibly and in accordance with your local laws and regulations.

## Author

[@kozydot](https://github.com/kozydot)