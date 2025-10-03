# Desktop Organizer MCP Server

MCP server for organizing files on your Mac Desktop by automatically categorizing them into folders.

## Features

- **List Desktop Files**: View all files on your Desktop grouped by category
- **Organize Desktop**: Move files into category folders (Images, Documents, Videos, etc.)
- **Preview Mode**: Dry-run option to preview changes before organizing
- **File Categorization**: Get the category for any file based on its extension

## Supported Categories

- **Images**: .jpg, .jpeg, .png, .gif, .bmp, .svg, .heic, .webp
- **Documents**: .pdf, .doc, .docx, .txt, .rtf, .pages, .odt
- **Spreadsheets**: .xls, .xlsx, .csv, .numbers, .ods
- **Presentations**: .ppt, .pptx, .key, .odp
- **Videos**: .mp4, .mov, .avi, .mkv, .wmv, .flv, .webm
- **Audio**: .mp3, .wav, .aac, .flac, .m4a, .ogg
- **Archives**: .zip, .rar, .7z, .tar, .gz, .bz2, .dmg
- **Code**: .py, .js, .java, .cpp, .c, .h, .swift, .go, .rs
- **Scripts**: .sh, .bat, .ps1, .zsh, .fish
- **Data**: .json, .xml, .yaml, .yml, .toml, .sql
- **Others**: Any files that don't match the above categories

## Setup

1. **Install dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install mcp
   ```

2. **Configure Claude Desktop**:

   Edit your Claude Desktop config file at:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

   Add this configuration:
   ```json
   {
     "mcpServers": {
       "desktop-organizer": {
         "command": "/Users/robertwatson/Code/desktop-organizer-mcp/venv/bin/python",
         "args": ["/Users/robertwatson/Code/desktop-organizer-mcp/src/server.py"]
       }
     }
   }
   ```

3. **Restart Claude Desktop** to load the MCP server

## Available Tools

### `list_desktop_files`
Lists all files on your Desktop grouped by category.

**Example**: "Show me what files are on my Desktop"

### `organize_desktop`
Organizes Desktop files by moving them into category folders.

**Parameters**:
- `dry_run` (boolean, optional): Preview changes without moving files (default: false)

**Examples**:
- "Organize my Desktop files" - Actually moves files
- "Show me how my Desktop would be organized" - Dry run preview

### `get_file_category`
Get the category for a specific file.

**Parameters**:
- `filename` (string, required): The filename to categorize

**Example**: "What category is report.pdf?"

## Usage Examples

Once configured in Claude Desktop, you can ask:

- "What files are on my Desktop?"
- "Organize my Desktop files"
- "Show me a preview of how my Desktop would be organized"
- "What category would screenshot.png be in?"

## Development

Run the server directly for testing:
```bash
source venv/bin/activate
python src/server.py
```
