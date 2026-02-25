"""Statistics panel for displaying task completion status."""
import tkinter as tk
from tkinter import ttk

from ..managers.statistics_module import StatisticsModule


class StatsPanel:
    """Panel displaying task statistics with minimalist design."""
    
    def __init__(self, parent, statistics_module: StatisticsModule):
        self.statistics_module = statistics_module
        
        self.frame = ttk.Frame(parent)
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self) -> None:
        """Set up statistics panel UI."""
        # Stats container
        stats_frame = ttk.Frame(self.frame)
        stats_frame.pack(fill=tk.X)
        
        # Total tasks
        self.total_label = ttk.Label(stats_frame, text="总任务: 0", style="Stats.TLabel")
        self.total_label.pack(side=tk.LEFT, padx=15)
        
        # Completed
        self.completed_label = ttk.Label(stats_frame, text="已完成: 0", style="Stats.TLabel")
        self.completed_label.pack(side=tk.LEFT, padx=15)
        
        # Pending
        self.pending_label = ttk.Label(stats_frame, text="待完成: 0", style="Stats.TLabel")
        self.pending_label.pack(side=tk.LEFT, padx=15)
        
        # Overdue
        self.overdue_label = ttk.Label(stats_frame, text="已过期: 0", style="Stats.TLabel")
        self.overdue_label.pack(side=tk.LEFT, padx=15)
        
        # Progress bar
        progress_frame = ttk.Frame(self.frame)
        progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(progress_frame, text="完成进度:").pack(side=tk.LEFT)
        self.progress_bar = ttk.Progressbar(progress_frame, length=200, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, padx=10)
        self.percent_label = ttk.Label(progress_frame, text="0%")
        self.percent_label.pack(side=tk.LEFT)
    
    def refresh(self) -> None:
        """Refresh statistics display."""
        stats = self.statistics_module.get_statistics_summary()
        
        self.total_label.config(text=f"总任务: {stats['total']}")
        self.completed_label.config(text=f"已完成: {stats['completed']}")
        self.pending_label.config(text=f"待完成: {stats['pending']}")
        
        # Highlight overdue if any
        overdue = stats['overdue']
        if overdue > 0:
            self.overdue_label.config(text=f"⚠ 已过期: {overdue}", foreground="#E74C3C")
        else:
            self.overdue_label.config(text=f"已过期: {overdue}", foreground="#333333")
        
        # Update progress bar
        percentage = stats['completion_percentage']
        self.progress_bar['value'] = percentage
        self.percent_label.config(text=f"{percentage:.0f}%")
