"""Main window for personal workbench application."""
import tkinter as tk
from tkinter import ttk

from .task_panel import TaskPanel
from .link_panel import LinkPanel
from .stats_panel import StatsPanel
from ..managers.task_manager import TaskManager
from ..managers.link_manager import LinkManager
from ..managers.statistics_module import StatisticsModule


class MainWindow:
    """Main application window with minimalist design."""
    
    # Color scheme - minimalist
    BG_COLOR = "#FAFAFA"
    ACCENT_COLOR = "#4A90D9"
    TEXT_COLOR = "#333333"
    SECONDARY_TEXT = "#666666"
    
    def __init__(self, task_manager: TaskManager, link_manager: LinkManager, 
                 statistics_module: StatisticsModule):
        self.task_manager = task_manager
        self.link_manager = link_manager
        self.statistics_module = statistics_module
        
        self.root = tk.Tk()
        self.root.title("个人工作台")
        self.root.geometry("900x600")
        self.root.configure(bg=self.BG_COLOR)
        
        self._setup_styles()
        self._setup_ui()
    
    def _setup_styles(self) -> None:
        """Configure ttk styles for minimalist look."""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TFrame", background=self.BG_COLOR)
        style.configure("TLabel", background=self.BG_COLOR, foreground=self.TEXT_COLOR)
        style.configure("TButton", padding=6)
        style.configure("Header.TLabel", font=("Microsoft YaHei UI", 14, "bold"))
        style.configure("Stats.TLabel", font=("Microsoft YaHei UI", 12))
    
    def _setup_ui(self) -> None:
        """Set up the main UI layout."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Label(main_frame, text="个人工作台", style="Header.TLabel")
        header.pack(pady=(0, 10))
        
        # Stats panel at top
        self.stats_panel = StatsPanel(main_frame, self.statistics_module)
        self.stats_panel.frame.pack(fill=tk.X, pady=(0, 10))
        
        # Content area with notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Task panel tab
        self.task_panel = TaskPanel(notebook, self.task_manager, self._on_task_change)
        notebook.add(self.task_panel.frame, text="任务管理")
        
        # Link panel tab
        self.link_panel = LinkPanel(notebook, self.link_manager)
        notebook.add(self.link_panel.frame, text="常用链接")
    
    def _on_task_change(self) -> None:
        """Callback when tasks change to update statistics."""
        self.stats_panel.refresh()
    
    def refresh_all(self) -> None:
        """Refresh all panels."""
        self.task_panel.refresh()
        self.link_panel.refresh()
        self.stats_panel.refresh()
    
    def run(self) -> None:
        """Start the application main loop."""
        self.root.mainloop()
