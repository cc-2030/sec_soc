"""Storage module for data persistence using JSON files."""
import json
import os
import shutil
from datetime import datetime
from typing import List


class Storage:
    """Handles JSON file storage for tasks and links."""
    
    def __init__(self, file_path: str = "workbench_data.json"):
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Create storage file if it doesn't exist."""
        if not os.path.exists(self.file_path):
            self._create_empty_storage()
    
    def _create_empty_storage(self) -> None:
        """Create a new empty storage file."""
        data = {
            "version": "1.0",
            "tasks": [],
            "links": []
        }
        self._write_file(data)
    
    def _write_file(self, data: dict) -> bool:
        """Write data to JSON file."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            raise IOError(f"Failed to write storage file: {e}")
    
    def _backup_corrupted_file(self) -> None:
        """Backup corrupted file before creating new storage."""
        if os.path.exists(self.file_path):
            backup_path = f"{self.file_path}.corrupted.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.copy2(self.file_path, backup_path)
    
    def load(self) -> dict:
        """Load all data from storage file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            self._backup_corrupted_file()
            self._create_empty_storage()
            return {"version": "1.0", "tasks": [], "links": []}
        except FileNotFoundError:
            self._create_empty_storage()
            return {"version": "1.0", "tasks": [], "links": []}
    
    def save(self, data: dict) -> bool:
        """Save all data to storage file."""
        return self._write_file(data)
    
    def get_tasks(self) -> List[dict]:
        """Get all tasks from storage."""
        data = self.load()
        return data.get("tasks", [])
    
    def save_tasks(self, tasks: List[dict]) -> bool:
        """Save tasks to storage."""
        data = self.load()
        data["tasks"] = tasks
        return self.save(data)
    
    def get_links(self) -> List[dict]:
        """Get all links from storage."""
        data = self.load()
        return data.get("links", [])
    
    def save_links(self, links: List[dict]) -> bool:
        """Save links to storage."""
        data = self.load()
        data["links"] = links
        return self.save(data)
