"""Statistics module for task completion tracking."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .task_manager import TaskManager


class StatisticsModule:
    """Calculates and provides task statistics."""
    
    def __init__(self, task_manager: 'TaskManager'):
        self.task_manager = task_manager
    
    def get_total_count(self) -> int:
        """Get total number of tasks."""
        return len(self.task_manager.get_all_tasks())
    
    def get_completed_count(self) -> int:
        """Get number of completed tasks."""
        return len(self.task_manager.get_completed_tasks())
    
    def get_pending_count(self) -> int:
        """Get number of pending tasks."""
        return len(self.task_manager.get_pending_tasks())
    
    def get_overdue_count(self) -> int:
        """Get number of overdue tasks."""
        return len(self.task_manager.get_overdue_tasks())
    
    def get_completion_percentage(self) -> float:
        """Calculate completion percentage (0-100)."""
        total = self.get_total_count()
        if total == 0:
            return 0.0
        return (self.get_completed_count() / total) * 100
    
    def get_statistics_summary(self) -> dict:
        """Get a summary of all statistics."""
        return {
            "total": self.get_total_count(),
            "completed": self.get_completed_count(),
            "pending": self.get_pending_count(),
            "overdue": self.get_overdue_count(),
            "completion_percentage": self.get_completion_percentage()
        }
