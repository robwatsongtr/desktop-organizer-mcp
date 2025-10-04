#!/usr/bin/env python3
"""
MCP Server for organizing Mac Desktop files.

This server demonstrates the Model Context Protocol (MCP) by exposing tools
that allow an LLM to interact with the file system to organize desktop files.

Key MCP Concepts:
- Server: The main application that exposes tools to the LLM client
- Tools: Functions that the LLM can call to perform actions
- stdio: Communication happens via standard input/output (stdin/stdout)
"""

import asyncio
import json
from pathlib import Path

# MCP SDK imports - these provide the building blocks for creating an MCP server
from mcp.server import Server  # The main server class
from mcp.server.stdio import stdio_server  # Handles stdin/stdout communication
from mcp.types import Tool, TextContent  # Type definitions for tools and responses

from organizer import FileOrganizer


# Create the MCP server instance with a unique name
# This name identifies your server to the MCP client (Claude Desktop)
app = Server("desktop-organizer")

# Initialize our file organizer - this handles the actual file system operations
organizer = FileOrganizer()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    MCP Protocol Handler: Tool Discovery

    This decorator (@app.list_tools) tells the MCP server to call this function
    when the client (Claude Desktop) asks "what tools are available?"

    The LLM uses this list to know what actions it can take. Each tool needs:
    - name: Unique identifier for the tool
    - description: Tells the LLM what the tool does and when to use it
    - inputSchema: JSON Schema defining the parameters (like a function signature)

    Think of this as the "menu" of capabilities you're giving to the LLM.

    Me: Based on a natural language input from the client, the LLM decides which tool 
    best fits?
    """
    return [
        Tool(
            name="list_desktop_files",
            # Clear description helps the LLM know when to call this tool
            description="List all files on the Desktop grouped by category (Images, Documents, Videos, etc.)",
            inputSchema={
                "type": "object",
                "properties": {},  # No parameters needed for this tool
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
                # Note: dry_run is optional, so no "required" field
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
                # This parameter is required - the LLM must provide it
                "required": ["filename"],
            },
        ),
        Tool(
            name="organize_things_from_desktop",
            description="Organize files from the things_from_desktop folder by moving them into category folders on Desktop",
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
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    MCP Protocol Handler: Tool Execution

    This decorator (@app.call_tool) tells the MCP server to call this function
    when the LLM decides to use one of your tools.

    Flow:
    1. LLM reads user request: "What files are on my Desktop?"
    2. LLM sees the list_desktop_files tool from list_tools()
    3. LLM calls this function with name="list_desktop_files" and arguments={}
    4. Your code executes and returns results to the LLM
    5. LLM uses the results to respond to the user

    Parameters:
    - name: Which tool the LLM wants to call
    - arguments: The parameters the LLM is passing (based on inputSchema)

    Returns:
    - list[TextContent]: The results to send back to the LLM
    """

    if name == "list_desktop_files":
        # Call our organizer to get files grouped by category
        categorized = organizer.get_files_by_category()

        if not categorized:
            # Return a TextContent object - this is what the LLM will see
            return [TextContent(
                type="text",
                text="No files found on Desktop, or Desktop path does not exist."
            )]

        # Format the results in a nice way for the LLM to read and present to user
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

        # Always return a list of TextContent objects
        return [TextContent(type="text", text=result)]

    elif name == "organize_desktop":
        # Extract parameters from the arguments dict that the LLM provided
        # The LLM decided whether to set dry_run based on user's request
        dry_run = arguments.get("dry_run", False)

        # Execute the file organization (or preview if dry_run=True)
        # SIMPLIFIED: organizer now returns a ready-to-use string message
        message = organizer.organize_files(dry_run=dry_run)

        # Just pass the message directly to the LLM
        # No need for complex formatting - the organizer handles it
        return [TextContent(type="text", text=message)]

    elif name == "get_file_category":
        # Get the filename parameter that the LLM extracted from user's question
        filename = arguments.get("filename")

        # Validate required parameters (though the schema should enforce this)
        if not filename:
            return [TextContent(
                type="text",
                text="Error: filename parameter is required"
            )]

        # Use our organizer to categorize the file
        category = organizer.categorize_file(filename)

        # Return the category information to the LLM
        return [TextContent(
            type="text",
            text=f"File: {filename}\nCategory: {category}"
        )]

    elif name == "organize_things_from_desktop":
        dry_run = arguments.get("dry_run", False)

        # TODO: Implement organize_things_folder method
        message = organizer.organize_things_folder(dry_run=dry_run)

        return [TextContent(type="text", text=message)]

    # Fallback if an unknown tool name is requested (shouldn't happen normally)
    return [TextContent(
        type="text",
        text=f"Unknown tool: {name}"
    )]


async def main():
    """
    Main entry point for the MCP server.

    MCP servers communicate via stdin/stdout (standard input/output):
    - Claude Desktop sends requests via stdin (e.g., "list tools", "call tool X")
    - Our server sends responses via stdout (e.g., tool results, error messages)

    This is why you don't see any HTTP servers or network ports - MCP uses
    simple process communication. Claude Desktop launches this Python process
    and talks to it directly.

    The stdio_server() context manager sets up the communication channels,
    and app.run() starts the main server loop that handles requests.
    """
    async with stdio_server() as (read_stream, write_stream):
        # Run the MCP server, handling requests from Claude Desktop
        await app.run(
            read_stream,   # Where we receive requests from Claude Desktop
            write_stream,  # Where we send responses back to Claude Desktop
            app.create_initialization_options()  # Server configuration
        )


if __name__ == "__main__":
    # Start the async event loop and run our MCP server
    # This keeps running until Claude Desktop closes the connection
    asyncio.run(main())
