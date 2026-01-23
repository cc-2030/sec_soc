"""Link data model for personal workbench."""
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Link:
    """Represents a web link with name and URL."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    url: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Serialize link to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Link':
        """Deserialize link from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            url=data["url"],
            created_at=datetime.fromisoformat(data["created_at"])
        )
