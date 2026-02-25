"""Task data model for personal workbench."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid


class TaskStatus(Enum):
    """Task status enumeration."""
    NEW = "new"           # 新建
    COMPLETED = "completed"  # 完成
    OVERDUE = "overdue"   # 超时
    IGNORED = "ignored"   # 忽略


class TaskPriority(Enum):
    """Task priority enumeration."""
    LOW = "low"           # 低
    MEDIUM = "medium"     # 中
    HIGH = "high"         # 高
    URGENT = "urgent"     # 紧急


@dataclass
class Task:
    """Represents a task with full lifecycle tracking."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    category: str = ""  # 分类/标签
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    status: TaskStatus = TaskStatus.NEW
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    ignored_at: Optional[datetime] = None
    ignore_reason: str = ""
    
    def to_dict(self) -> dict:
        """Serialize task to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority.value,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "ignored_at": self.ignored_at.isoformat() if self.ignored_at else None,
            "ignore_reason": self.ignore_reason
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Deserialize task from dictionary."""
        status_value = data.get("status", "new")
        if "completed" in data and data["completed"] and status_value == "new":
            status_value = "completed"
        
        priority_value = data.get("priority", "medium")
        
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            category=data.get("category", ""),
            priority=TaskPriority(priority_value),
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            status=TaskStatus(status_value),
            created_at=datetime.fromisoformat(data["created_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            ignored_at=datetime.fromisoformat(data["ignored_at"]) if data.get("ignored_at") else None,
            ignore_reason=data.get("ignore_reason", "")
        )
    
    def is_overdue(self) -> bool:
        """Check if task is overdue (past due date and still new)."""
        if self.status != TaskStatus.NEW or self.due_date is None:
            return False
        return datetime.now() > self.due_date
    
    def check_and_update_overdue(self) -> None:
        """Auto-update status to overdue if past due date."""
        if self.is_overdue():
            self.status = TaskStatus.OVERDUE
