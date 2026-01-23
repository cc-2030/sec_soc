"""Link manager for handling link operations."""
import re
import webbrowser
from datetime import datetime
from typing import List, Optional

from ..models.link import Link
from ..storage.storage import Storage


class LinkManager:
    """Manages link CRUD operations."""
    
    URL_PATTERN = re.compile(r'^https?://.+')
    
    def __init__(self, storage: Storage):
        self.storage = storage
        self._links: dict[str, Link] = {}
        self._load_links()
    
    def _load_links(self) -> None:
        """Load links from storage."""
        link_dicts = self.storage.get_links()
        self._links = {l["id"]: Link.from_dict(l) for l in link_dicts}
    
    def _save_links(self) -> None:
        """Save links to storage."""
        link_dicts = [l.to_dict() for l in self._links.values()]
        self.storage.save_links(link_dicts)
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format (must start with http:// or https://)."""
        return bool(LinkManager.URL_PATTERN.match(url))
    
    def add_link(self, name: str, url: str) -> Link:
        """Add a new link with validation."""
        if not name or not name.strip():
            raise ValueError("Link name cannot be empty")
        
        if not self.validate_url(url):
            raise ValueError("Invalid URL format")
        
        link = Link(
            name=name.strip(),
            url=url,
            created_at=datetime.now()
        )
        self._links[link.id] = link
        self._save_links()
        return link
    
    def update_link(self, link_id: str, **kwargs) -> Link:
        """Update an existing link."""
        if link_id not in self._links:
            raise KeyError("Link not found")
        
        link = self._links[link_id]
        
        if "name" in kwargs:
            new_name = kwargs["name"]
            if not new_name or not new_name.strip():
                raise ValueError("Link name cannot be empty")
            link.name = new_name.strip()
        
        if "url" in kwargs:
            new_url = kwargs["url"]
            if not self.validate_url(new_url):
                raise ValueError("Invalid URL format")
            link.url = new_url
        
        self._save_links()
        return link
    
    def delete_link(self, link_id: str) -> bool:
        """Delete a link by ID."""
        if link_id not in self._links:
            raise KeyError("Link not found")
        
        del self._links[link_id]
        self._save_links()
        return True
    
    def get_all_links(self) -> List[Link]:
        """Get all links."""
        return list(self._links.values())
    
    def get_link_by_id(self, link_id: str) -> Optional[Link]:
        """Get a link by ID."""
        return self._links.get(link_id)
    
    def open_link(self, link_id: str) -> bool:
        """Open a link in the default browser."""
        if link_id not in self._links:
            raise KeyError("Link not found")
        
        link = self._links[link_id]
        webbrowser.open(link.url)
        return True
