"""Link data model for personal workbench."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import uuid


@dataclass
class Link:
    """Represents a web link with name, URL, category and tags."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    url: str = ""
    category: str = ""  # 分类
    tags: List[str] = field(default_factory=list)  # 标签
    icon: str = ""  # 图标(emoji或首字母)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Serialize link to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "category": self.category,
            "tags": self.tags,
            "icon": self.icon,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Link':
        """Deserialize link from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            url=data["url"],
            category=data.get("category", ""),
            tags=data.get("tags", []),
            icon=data.get("icon", ""),
            created_at=datetime.fromisoformat(data["created_at"])
        )
