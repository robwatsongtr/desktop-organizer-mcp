"""
File Organizer Module

This module contains the business logic for file categorization and organization.
It's separate from the MCP server code (server.py) to maintain clean separation
of concerns:
- server.py: Handles MCP protocol communication with Claude Desktop
- organizer.py: Contains the actual file system logic

This separation makes the code more testable and reusable.
"""

import os
from pathlib import Path
from typing import Dict, List


class FileOrganizer:
    """
    Handles file categorization and organization logic.

    This class doesn't know anything about MCP - it just provides methods
    to categorize and organize files. The MCP server calls these methods
    when the LLM requests tool execution.
    """

    # Category definitions: maps category names to file extensions
    # SIMPLIFIED: Just a few common categories to keep the example clear
    # You can easily extend this to support more file types
    CATEGORIES = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".heic", ".webp"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".pages"],
        "Videos": [".mp4", ".mov", ".avi"],
        "Code": [".py", ".js", ".java", ".cpp", ".go"],
    }

    def __init__(self, desktop_path: str = None):
        """
        Initialize the FileOrganizer.

        Args:
            desktop_path: Optional custom path to organize. Defaults to ~/Desktop
        """
        if desktop_path is None:
            # Default to the user's Desktop directory
            desktop_path = str(Path.home() / "Desktop")
        self.desktop_path = Path(desktop_path)

    def categorize_file(self, filename: str) -> str:
        """
        Determine the category for a file based on its extension.

        This is the core categorization logic. It extracts the file extension
        and matches it against our CATEGORIES dictionary.

        Args:
            filename: The name of the file to categorize (e.g., "report.pdf")

        Returns:
            The category name (e.g., "Documents") or "Others" if no match

        Example:
            categorize_file("vacation.jpg") -> "Images"
            categorize_file("report.pdf") -> "Documents"
            categorize_file("unknown.xyz") -> "Others"
        """
        # Extract file extension (e.g., ".pdf" from "report.pdf")
        # .lower() ensures case-insensitive matching (.PDF and .pdf both work)
        ext = Path(filename).suffix.lower()

        # Search through our categories to find a match
        for category, extensions in self.CATEGORIES.items():
            if ext in extensions:
                return category

        # If no category matches, return "Others"
        return "Others"

    def get_files_by_category(self) -> Dict[str, List[str]]:
        """
        Group all files on the Desktop by category.

        This method scans the Desktop directory and builds a dictionary
        mapping each category to a list of files in that category.

        Returns:
            Dictionary mapping category names to lists of filenames
            Example: {"Images": ["photo.jpg", "logo.png"], "Documents": ["report.pdf"]}

        Note:
            - Ignores hidden files (those starting with ".")
            - Ignores directories
            - Returns empty dict if Desktop doesn't exist
        """
        categorized_files: Dict[str, List[str]] = {}

        # Check if Desktop path exists
        if not self.desktop_path.exists():
            return categorized_files

        # Iterate through all items in the Desktop directory
        for item in self.desktop_path.iterdir():
            # Only process files (not directories) and skip hidden files (starting with .)
            if item.is_file() and not item.name.startswith("."):
                # Categorize this file
                category = self.categorize_file(item.name)

                # Add file to the appropriate category list
                if category not in categorized_files:
                    categorized_files[category] = []
                categorized_files[category].append(item.name)

        return categorized_files

    def organize_files(self, dry_run: bool = False) -> str:
        """
        Organize files into category folders.

        SIMPLIFIED VERSION: Returns a formatted string message instead of complex dict.
        This keeps the focus on MCP concepts rather than data structure complexity.

        Args:
            dry_run: If True, simulates the organization without moving files.
                    Useful for previewing changes before committing.

        Returns:
            A human-readable string describing what happened (or would happen)

        Example flow (not dry_run):
            Desktop/
              photo.jpg
              report.pdf

            Becomes:
            Desktop/
              Images/
                photo.jpg
              Documents/
                report.pdf
        """
        # Get all files grouped by category
        categorized = self.get_files_by_category()

        if not categorized:
            return "No files to organize on Desktop."

        # Build the result message
        message_lines = []
        total_files = 0

        # Process each category
        for category, files in categorized.items():
            if not files:
                continue

            # Determine the destination folder (e.g., Desktop/Images/)
            category_folder = self.desktop_path / category

            # Create the category folder (unless this is a dry run)
            if not dry_run:
                category_folder.mkdir(exist_ok=True)  # exist_ok=True won't error if folder exists

            # Move each file into the category folder
            for filename in files:
                source = self.desktop_path / filename           # Current location
                destination = category_folder / filename        # Target location

                if not dry_run:
                    # Actually move the file
                    try:
                        source.rename(destination)  # Move/rename the file
                    except Exception as e:
                        # If move fails, include error in message
                        message_lines.append(f"❌ Error moving {filename}: {e}")
                        continue

                # Record what happened/would happen
                action = "would move" if dry_run else "moved"
                message_lines.append(f"  • {filename} → {category}/")
                total_files += 1

        # Build final message
        mode = "DRY RUN - Preview" if dry_run else "✓ Organization Complete"
        result = f"{mode}\n\n"
        result += "\n".join(message_lines)
        result += f"\n\nTotal: {total_files} files"

        if dry_run:
            result += "\n\n*Run with dry_run=false to actually move the files.*"

        return result
