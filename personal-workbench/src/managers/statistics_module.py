"""Statistics module for task completion tracking."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .task_manager import TaskManager


class StatisticsModule:
    """Calculates and provides task statistics."""
    
    def __init__(self, task_manager: 'TaskManager'):
        self.task_manager = task_manager
    
    def get_total_count(self, user_id: str = "") -> int:
        """Get total number of tasks."""
        return len(self.task_manager.get_all_tasks(user_id=user_id))
    
    def get_new_count(self, user_id: str = "") -> int:
        """Get number of new tasks."""
        return len(self.task_manager.get_new_tasks(user_id=user_id))
    
    def get_completed_count(self, user_id: str = "") -> int:
        """Get number of completed tasks."""
        return len(self.task_manager.get_completed_tasks(user_id=user_id))
    
    def get_overdue_count(self, user_id: str = "") -> int:
        """Get number of overdue tasks."""
        return len(self.task_manager.get_overdue_tasks(user_id=user_id))
    
    def get_ignored_count(self, user_id: str = "") -> int:
        """Get number of ignored tasks."""
        return len(self.task_manager.get_ignored_tasks(user_id=user_id))
    
    def get_completion_percentage(self, user_id: str = "") -> float:
        """Calculate completion percentage (0-100)."""
        total = self.get_total_count(user_id=user_id)
        if total == 0:
            return 0.0
        return (self.get_completed_count(user_id=user_id) / total) * 100
    
    def get_statistics_summary(self, user_id: str = "") -> dict:
        """Get a summary of all statistics."""
        return {
            "total": self.get_total_count(user_id=user_id),
            "new": self.get_new_count(user_id=user_id),
            "completed": self.get_completed_count(user_id=user_id),
            "overdue": self.get_overdue_count(user_id=user_id),
            "ignored": self.get_ignored_count(user_id=user_id),
            "completion_percentage": self.get_completion_percentage(user_id=user_id)
        }
