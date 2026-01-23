"""Task manager for handling task operations."""
from datetime import datetime
from typing import List, Optional

from ..models.task import Task
from ..storage.storage import Storage


class TaskManager:
    """Manages task CRUD operations and queries."""
    
    def __init__(self, storage: Storage):
        self.storage = storage
        self._tasks: dict[str, Task] = {}
        self._load_tasks()
    
    def _load_tasks(self) -> None:
        """Load tasks from storage."""
        task_dicts = self.storage.get_tasks()
        self._tasks = {t["id"]: Task.from_dict(t) for t in task_dicts}
    
    def _save_tasks(self) -> None:
        """Save tasks to storage."""
        task_dicts = [t.to_dict() for t in self._tasks.values()]
        self.storage.save_tasks(task_dicts)
    
    def create_task(self, title: str, description: str = "", 
                    due_date: Optional[datetime] = None) -> Task:
        """Create a new task with validation."""
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        
        task = Task(
            title=title.strip(),
            description=description,
            due_date=due_date,
            completed=False,
            created_at=datetime.now()
        )
        self._tasks[task.id] = task
        self._save_tasks()
        return task
    
    def update_task(self, task_id: str, **kwargs) -> Task:
        """Update an existing task."""
        if task_id not in self._tasks:
            raise KeyError("Task not found")
        
        task = self._tasks[task_id]
        
        if "title" in kwargs:
            new_title = kwargs["title"]
            if not new_title or not new_title.strip():
                raise ValueError("Task title cannot be empty")
            task.title = new_title.strip()
        
        if "description" in kwargs:
            task.description = kwargs["description"]
        
        if "due_date" in kwargs:
            task.due_date = kwargs["due_date"]
        
        self._save_tasks()
        return task
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID."""
        if task_id not in self._tasks:
            raise KeyError("Task not found")
        
        del self._tasks[task_id]
        self._save_tasks()
        return True
    
    def complete_task(self, task_id: str) -> Task:
        """Mark a task as completed."""
        if task_id not in self._tasks:
            raise KeyError("Task not found")
        
        task = self._tasks[task_id]
        task.completed = True
        task.completed_at = datetime.now()
        self._save_tasks()
        return task
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        return list(self._tasks.values())
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending (not completed) tasks."""
        return [t for t in self._tasks.values() if not t.completed]
    
    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks."""
        return [t for t in self._tasks.values() if t.completed]
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks."""
        return [t for t in self._tasks.values() if t.is_overdue()]
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self._tasks.get(task_id)
