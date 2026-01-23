"""Main entry point for Personal Workbench application."""
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.storage import Storage
from src.managers.task_manager import TaskManager
from src.managers.link_manager import LinkManager
from src.managers.statistics_module import StatisticsModule
from src.ui.main_window import MainWindow


def main():
    """Initialize and run the application."""
    # Initialize storage
    storage = Storage("workbench_data.json")
    
    # Initialize managers
    task_manager = TaskManager(storage)
    link_manager = LinkManager(storage)
    statistics_module = StatisticsModule(task_manager)
    
    # Create and run main window
    app = MainWindow(task_manager, link_manager, statistics_module)
    app.run()


if __name__ == "__main__":
    main()
