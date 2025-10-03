#!/usr/bin/env python3
"""MCP Server for organizing Mac Desktop files."""

import asyncio
import json
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from organizer import FileOrganizer


app = Server("desktop-organizer")
organizer = FileOrganizer()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for desktop organization."""
    return [
        Tool(
            name="list_desktop_files",
            description="List all files on the Desktop grouped by category (Images, Documents, Videos, etc.)",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="organize_desktop",
            description="Organize Desktop files by moving them into category folders. Use dry_run=true to preview changes without moving files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dry_run": {
                        "type": "boolean",
                        "description": "If true, preview changes without actually moving files",
                        "default": False,
                    },
                },
            },
        ),
        Tool(
            name="get_file_category",
            description="Get the category for a specific file based on its extension",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The filename to categorize",
                    },
                },
                "required": ["filename"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls for desktop organization."""

    if name == "list_desktop_files":
        categorized = organizer.get_files_by_category()

        if not categorized:
            return [TextContent(
                type="text",
                text="No files found on Desktop, or Desktop path does not exist."
            )]

        result = "Desktop Files by Category:\n\n"
        total_files = 0

        for category in sorted(categorized.keys()):
            files = categorized[category]
            result += f"**{category}** ({len(files)} files):\n"
            for file in sorted(files):
                result += f"  - {file}\n"
            result += "\n"
            total_files += len(files)

        result += f"Total: {total_files} files"

        return [TextContent(type="text", text=result)]

    elif name == "organize_desktop":
        dry_run = arguments.get("dry_run", False)
        results = organizer.organize_files(dry_run=dry_run)

        mode = "DRY RUN - Preview" if dry_run else "Organization Complete"
        result = f"**{mode}**\n\n"

        if results["created_folders"]:
            result += "Created/Used Folders:\n"
            for folder in results["created_folders"]:
                result += f"  - {folder}/\n"
            result += "\n"

        if results["moved_files"]:
            result += f"Files {'would be ' if dry_run else ''}moved:\n"
            for item in results["moved_files"]:
                action = "would move" if dry_run else "moved"
                result += f"  - {item['file']} → {item['category']}/\n"
            result += f"\nTotal: {len(results['moved_files'])} files\n"
        else:
            result += "No files to organize.\n"

        if results["errors"]:
            result += "\nErrors:\n"
            for error in results["errors"]:
                result += f"  - {error['file']}: {error['error']}\n"

        if dry_run:
            result += "\n*Run with dry_run=false to actually move the files.*"

        return [TextContent(type="text", text=result)]

    elif name == "get_file_category":
        filename = arguments.get("filename")

        if not filename:
            return [TextContent(
                type="text",
                text="Error: filename parameter is required"
            )]

        category = organizer.categorize_file(filename)

        return [TextContent(
            type="text",
            text=f"File: {filename}\nCategory: {category}"
        )]

    return [TextContent(
        type="text",
        text=f"Unknown tool: {name}"
    )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
