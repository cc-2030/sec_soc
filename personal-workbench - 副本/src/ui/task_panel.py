"""Task panel for managing tasks."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from typing import Callable, Optional

from ..managers.task_manager import TaskManager


class TaskPanel:
    """Panel for task management with add, edit, delete, complete functions."""
    
    OVERDUE_COLOR = "#E74C3C"
    COMPLETED_COLOR = "#27AE60"
    PENDING_COLOR = "#333333"
    
    def __init__(self, parent, task_manager: TaskManager, on_change: Callable = None):
        self.task_manager = task_manager
        self.on_change = on_change
        
        self.frame = ttk.Frame(parent, padding="10")
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self) -> None:
        """Set up task panel UI."""
        # Toolbar
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="+ 添加任务", command=self._add_task).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="完成", command=self._complete_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="编辑", command=self._edit_task).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="删除", command=self._delete_task).pack(side=tk.LEFT, padx=5)
        
        # Task list with scrollbar
        list_frame = ttk.Frame(self.frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.task_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                     font=("Microsoft YaHei UI", 10), selectmode=tk.SINGLE)
        self.task_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.task_list.yview)
        
        self._task_ids = []
    
    def refresh(self) -> None:
        """Refresh task list display."""
        self.task_list.delete(0, tk.END)
        self._task_ids = []
        
        # Pending tasks first
        pending = self.task_manager.get_pending_tasks()
        for task in sorted(pending, key=lambda t: t.due_date or datetime.max):
            idx = self.task_list.size()
            status = "⏳"
            due_str = f" (截止: {task.due_date.strftime('%m/%d')})" if task.due_date else ""
            self.task_list.insert(tk.END, f"{status} {task.title}{due_str}")
            self._task_ids.append(task.id)
            
            if task.is_overdue():
                self.task_list.itemconfig(idx, fg=self.OVERDUE_COLOR)
            else:
                self.task_list.itemconfig(idx, fg=self.PENDING_COLOR)
        
        # Completed tasks
        completed = self.task_manager.get_completed_tasks()
        for task in completed:
            idx = self.task_list.size()
            self.task_list.insert(tk.END, f"✓ {task.title}")
            self._task_ids.append(task.id)
            self.task_list.itemconfig(idx, fg=self.COMPLETED_COLOR)
    
    def _get_selected_task_id(self) -> Optional[str]:
        """Get currently selected task ID."""
        selection = self.task_list.curselection()
        if not selection:
            return None
        return self._task_ids[selection[0]]
    
    def _add_task(self) -> None:
        """Show dialog to add new task."""
        dialog = TaskDialog(self.frame, "添加任务")
        if dialog.result:
            try:
                self.task_manager.create_task(
                    title=dialog.result["title"],
                    description=dialog.result.get("description", ""),
                    due_date=dialog.result.get("due_date")
                )
                self.refresh()
                if self.on_change:
                    self.on_change()
            except ValueError as e:
                messagebox.showerror("错误", str(e))
    
    def _edit_task(self) -> None:
        """Edit selected task."""
        task_id = self._get_selected_task_id()
        if not task_id:
            messagebox.showwarning("提示", "请先选择一个任务")
            return
        
        task = self.task_manager.get_task_by_id(task_id)
        if not task:
            return
        
        dialog = TaskDialog(self.frame, "编辑任务", task.title, task.description, task.due_date)
        if dialog.result:
            try:
                self.task_manager.update_task(
                    task_id,
                    title=dialog.result["title"],
                    description=dialog.result.get("description", ""),
                    due_date=dialog.result.get("due_date")
                )
                self.refresh()
                if self.on_change:
                    self.on_change()
            except (ValueError, KeyError) as e:
                messagebox.showerror("错误", str(e))
    
    def _delete_task(self) -> None:
        """Delete selected task."""
        task_id = self._get_selected_task_id()
        if not task_id:
            messagebox.showwarning("提示", "请先选择一个任务")
            return
        
        if messagebox.askyesno("确认", "确定要删除这个任务吗？"):
            try:
                self.task_manager.delete_task(task_id)
                self.refresh()
                if self.on_change:
                    self.on_change()
            except KeyError as e:
                messagebox.showerror("错误", str(e))
    
    def _complete_task(self) -> None:
        """Mark selected task as complete."""
        task_id = self._get_selected_task_id()
        if not task_id:
            messagebox.showwarning("提示", "请先选择一个任务")
            return
        
        task = self.task_manager.get_task_by_id(task_id)
        if task and task.completed:
            messagebox.showinfo("提示", "该任务已完成")
            return
        
        try:
            self.task_manager.complete_task(task_id)
            self.refresh()
            if self.on_change:
                self.on_change()
        except KeyError as e:
            messagebox.showerror("错误", str(e))


class TaskDialog:
    """Dialog for adding/editing tasks."""
    
    def __init__(self, parent, title: str, task_title: str = "", 
                 description: str = "", due_date: datetime = None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("350x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Title
        ttk.Label(self.dialog, text="标题:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.title_entry = ttk.Entry(self.dialog, width=35)
        self.title_entry.grid(row=0, column=1, padx=10, pady=5)
        self.title_entry.insert(0, task_title)
        
        # Description
        ttk.Label(self.dialog, text="描述:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.desc_entry = ttk.Entry(self.dialog, width=35)
        self.desc_entry.grid(row=1, column=1, padx=10, pady=5)
        self.desc_entry.insert(0, description)
        
        # Due date
        ttk.Label(self.dialog, text="截止日期:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.date_entry = ttk.Entry(self.dialog, width=35)
        self.date_entry.grid(row=2, column=1, padx=10, pady=5)
        if due_date:
            self.date_entry.insert(0, due_date.strftime("%Y-%m-%d"))
        ttk.Label(self.dialog, text="(格式: YYYY-MM-DD)").grid(row=3, column=1, sticky="w", padx=10)
        
        # Buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="确定", command=self._on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self._on_cancel).pack(side=tk.LEFT)
        
        self.dialog.wait_window()
    
    def _on_ok(self) -> None:
        """Handle OK button."""
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("错误", "标题不能为空")
            return
        
        due_date = None
        date_str = self.date_entry.get().strip()
        if date_str:
            try:
                due_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("错误", "日期格式不正确，请使用 YYYY-MM-DD")
                return
        
        self.result = {
            "title": title,
            "description": self.desc_entry.get().strip(),
            "due_date": due_date
        }
        self.dialog.destroy()
    
    def _on_cancel(self) -> None:
        """Handle Cancel button."""
        self.dialog.destroy()
