"""Task manager for handling task operations."""
from datetime import datetime
from typing import List, Optional, Tuple

from ..models.task import Task, TaskStatus, TaskPriority
from ..storage.storage import Storage


class TaskManager:
    """Manages task CRUD operations and queries."""
    
    PRIORITY_ORDER = {TaskPriority.URGENT: 0, TaskPriority.HIGH: 1, TaskPriority.MEDIUM: 2, TaskPriority.LOW: 3}
    
    def __init__(self, storage: Storage):
        self.storage = storage
        self._tasks: dict[str, Task] = {}
        self._load_tasks()
    
    def _load_tasks(self) -> None:
        """Load tasks from storage."""
        task_dicts = self.storage.get_tasks()
        self._tasks = {t["id"]: Task.from_dict(t) for t in task_dicts}
        for task in self._tasks.values():
            task.check_and_update_overdue()
        self._save_tasks()
    
    def _save_tasks(self) -> None:
        """Save tasks to storage."""
        task_dicts = [t.to_dict() for t in self._tasks.values()]
        self.storage.save_tasks(task_dicts)
    
    def create_task(self, title: str, description: str = "", due_date: Optional[datetime] = None,
                    category: str = "", priority: str = "medium") -> Task:
        """Create a new task with validation."""
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        
        task = Task(
            title=title.strip(),
            description=description,
            category=category.strip(),
            priority=TaskPriority(priority),
            due_date=due_date,
            status=TaskStatus.NEW,
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
        
        if "category" in kwargs:
            task.category = kwargs["category"].strip()
        
        if "priority" in kwargs:
            task.priority = TaskPriority(kwargs["priority"])
        
        self._save_tasks()
        return task
    
    def set_status(self, task_id: str, status: TaskStatus) -> Task:
        """Set task status."""
        if task_id not in self._tasks:
            raise KeyError("Task not found")
        
        task = self._tasks[task_id]
        task.status = status
        
        if status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now()
        
        self._save_tasks()
        return task
    
    def complete_task(self, task_id: str) -> Task:
        """Mark a task as completed."""
        return self.set_status(task_id, TaskStatus.COMPLETED)
    
    def ignore_task(self, task_id: str, reason: str = "") -> Task:
        """Mark a task as ignored with optional reason."""
        if task_id not in self._tasks:
            raise KeyError("Task not found")
        
        task = self._tasks[task_id]
        task.status = TaskStatus.IGNORED
        task.ignored_at = datetime.now()
        task.ignore_reason = reason
        
        self._save_tasks()
        return task
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        for task in self._tasks.values():
            task.check_and_update_overdue()
        return list(self._tasks.values())
    
    def get_tasks_paginated(self, page: int = 1, per_page: int = 20, 
                           status: Optional[TaskStatus] = None,
                           category: Optional[str] = None,
                           priority: Optional[TaskPriority] = None,
                           search: str = "",
                           sort_by: str = "created_at",
                           sort_order: str = "desc") -> Tuple[List[Task], int, int]:
        """Get tasks with pagination, filtering, and sorting."""
        tasks = self.get_all_tasks()
        
        # Filter by status
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        # Filter by category
        if category:
            tasks = [t for t in tasks if t.category == category]
        
        # Filter by priority
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        
        # Search in title and description
        if search:
            search_lower = search.lower()
            tasks = [t for t in tasks if search_lower in t.title.lower() or search_lower in t.description.lower()]
        
        # Sort
        reverse = sort_order == "desc"
        if sort_by == "priority":
            tasks.sort(key=lambda t: self.PRIORITY_ORDER.get(t.priority, 2), reverse=not reverse)
        elif sort_by == "due_date":
            tasks.sort(key=lambda t: t.due_date or datetime.max, reverse=reverse)
        elif sort_by == "title":
            tasks.sort(key=lambda t: t.title.lower(), reverse=reverse)
        else:  # created_at
            tasks.sort(key=lambda t: t.created_at, reverse=reverse)
        
        # Pagination
        total = len(tasks)
        total_pages = (total + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page
        
        return tasks[start:end], total, total_pages
    
    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        categories = set()
        for task in self._tasks.values():
            if task.category:
                categories.add(task.category)
        return sorted(categories)
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by status."""
        return [t for t in self.get_all_tasks() if t.status == status]
    
    def get_new_tasks(self) -> List[Task]:
        return self.get_tasks_by_status(TaskStatus.NEW)
    
    def get_completed_tasks(self) -> List[Task]:
        return self.get_tasks_by_status(TaskStatus.COMPLETED)
    
    def get_overdue_tasks(self) -> List[Task]:
        return self.get_tasks_by_status(TaskStatus.OVERDUE)
    
    def get_ignored_tasks(self) -> List[Task]:
        return self.get_tasks_by_status(TaskStatus.IGNORED)
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)
