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
            desktop_path = str(Path.home() / "Desktop")
        self.desktop_path = Path(desktop_path)

    def categorize_file(self, filename: str) -> str:
        """
        Determine the category for a file based on its extension.

        Args:
            filename: The name of the file to categorize (e.g., "report.pdf")

        Returns:
            The category name (e.g., "Documents") or "Others" if no match

        Example:
            categorize_file("vacation.jpg") -> "Images"
            categorize_file("report.pdf") -> "Documents"
            categorize_file("unknown.xyz") -> "Others"
        """
        ext = Path(filename).suffix.lower()

        for category, extensions in self.CATEGORIES.items():
            if ext in extensions:
                return category

        return "Others"

    def get_files_by_category(self) -> Dict[str, List[str]]:
        """
        Group all files on the Desktop by category.

        Returns:
            Dictionary mapping category names to lists of filenames
            Example: {"Images": ["photo.jpg", "logo.png"], "Documents": ["report.pdf"]}

        Note:
            - Ignores hidden files (those starting with ".")
            - Ignores directories
            - Returns empty dict if Desktop doesn't exist
        """
        categorized_files: Dict[str, List[str]] = {}

        if not self.desktop_path.exists():
            return categorized_files

        for item in self.desktop_path.iterdir():
            if item.is_file() and not item.name.startswith("."):
                category = self.categorize_file(item.name)
                if category not in categorized_files:
                    categorized_files[category] = []
                categorized_files[category].append(item.name)

        return categorized_files

    def organize_files(self, dry_run: bool = False) -> str:
        """
        Organize files into category folders.

        Args:
            dry_run: If True, simulates the organization without moving files.

        Returns:
            A human-readable string describing what happened (or would happen)
        """
        categorized = self.get_files_by_category()

        if not categorized:
            return "No files to organize on Desktop."

        message_lines = []
        total_files = 0

        for category, files in categorized.items():
            if not files:
                continue

            category_folder = self.desktop_path / category

            if not dry_run:
                category_folder.mkdir(exist_ok=True)

            for filename in files:
                source = self.desktop_path / filename
                destination = category_folder / filename

                if not dry_run:
                    try:
                        source.rename(destination)
                    except Exception as e:
                        message_lines.append(f"❌ Error moving {filename}: {e}")
                        continue

                message_lines.append(f"  • {filename} → {category}/")
                total_files += 1

        mode = "DRY RUN - Preview" if dry_run else "✓ Organization Complete"
        result = f"{mode}\n\n"
        result += "\n".join(message_lines)
        result += f"\n\nTotal: {total_files} files"

        if dry_run:
            result += "\n\n*Run with dry_run=false to actually move the files.*"

        return result
