import os
from pathlib import Path
from typing import Dict, List


class FileOrganizer:
    """Handles file categorization and organization logic."""

    CATEGORIES = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".heic", ".webp"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".pages", ".odt"],
        "Spreadsheets": [".xls", ".xlsx", ".csv", ".numbers", ".ods"],
        "Presentations": [".ppt", ".pptx", ".key", ".odp"],
        "Videos": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm"],
        "Audio": [".mp3", ".wav", ".aac", ".flac", ".m4a", ".ogg"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".dmg"],
        "Code": [".py", ".js", ".java", ".cpp", ".c", ".h", ".swift", ".go", ".rs"],
        "Scripts": [".sh", ".bat", ".ps1", ".zsh", ".fish"],
        "Data": [".json", ".xml", ".yaml", ".yml", ".toml", ".sql"],
    }

    def __init__(self, desktop_path: str = None):
        if desktop_path is None:
            desktop_path = str(Path.home() / "Desktop")
        self.desktop_path = Path(desktop_path)

    def categorize_file(self, filename: str) -> str:
        """Determine the category for a file based on its extension."""
        ext = Path(filename).suffix.lower()

        for category, extensions in self.CATEGORIES.items():
            if ext in extensions:
                return category

        return "Others"

    def get_files_by_category(self) -> Dict[str, List[str]]:
        """Group all files on the Desktop by category."""
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

    def organize_files(self, dry_run: bool = False) -> Dict[str, any]:
        """Organize files into category folders."""
        results = {
            "created_folders": [],
            "moved_files": [],
            "errors": [],
        }

        categorized = self.get_files_by_category()

        for category, files in categorized.items():
            if not files:
                continue

            category_folder = self.desktop_path / category

            if not dry_run:
                category_folder.mkdir(exist_ok=True)
                if category not in results["created_folders"]:
                    results["created_folders"].append(category)

            for filename in files:
                source = self.desktop_path / filename
                destination = category_folder / filename

                if dry_run:
                    results["moved_files"].append({
                        "file": filename,
                        "category": category,
                        "action": "would_move"
                    })
                else:
                    try:
                        source.rename(destination)
                        results["moved_files"].append({
                            "file": filename,
                            "category": category,
                            "action": "moved"
                        })
                    except Exception as e:
                        results["errors"].append({
                            "file": filename,
                            "error": str(e)
                        })

        return results
