"""Link panel for managing web links."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from ..managers.link_manager import LinkManager


class LinkPanel:
    """Panel for link management with add, edit, delete, open functions."""
    
    def __init__(self, parent, link_manager: LinkManager):
        self.link_manager = link_manager
        
        self.frame = ttk.Frame(parent, padding="10")
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self) -> None:
        """Set up link panel UI."""
        # Toolbar
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="+ 添加链接", command=self._add_link).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="打开", command=self._open_link).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="编辑", command=self._edit_link).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="删除", command=self._delete_link).pack(side=tk.LEFT, padx=5)
        
        # Link list with scrollbar
        list_frame = ttk.Frame(self.frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.link_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                     font=("Microsoft YaHei UI", 10), selectmode=tk.SINGLE)
        self.link_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.link_list.yview)
        
        # Double-click to open
        self.link_list.bind("<Double-1>", lambda e: self._open_link())
        
        self._link_ids = []
    
    def refresh(self) -> None:
        """Refresh link list display."""
        self.link_list.delete(0, tk.END)
        self._link_ids = []
        
        links = self.link_manager.get_all_links()
        for link in links:
            self.link_list.insert(tk.END, f"🔗 {link.name}")
            self._link_ids.append(link.id)
    
    def _get_selected_link_id(self) -> Optional[str]:
        """Get currently selected link ID."""
        selection = self.link_list.curselection()
        if not selection:
            return None
        return self._link_ids[selection[0]]
    
    def _add_link(self) -> None:
        """Show dialog to add new link."""
        dialog = LinkDialog(self.frame, "添加链接")
        if dialog.result:
            try:
                self.link_manager.add_link(
                    name=dialog.result["name"],
                    url=dialog.result["url"]
                )
                self.refresh()
            except ValueError as e:
                messagebox.showerror("错误", str(e))
    
    def _edit_link(self) -> None:
        """Edit selected link."""
        link_id = self._get_selected_link_id()
        if not link_id:
            messagebox.showwarning("提示", "请先选择一个链接")
            return
        
        link = self.link_manager.get_link_by_id(link_id)
        if not link:
            return
        
        dialog = LinkDialog(self.frame, "编辑链接", link.name, link.url)
        if dialog.result:
            try:
                self.link_manager.update_link(
                    link_id,
                    name=dialog.result["name"],
                    url=dialog.result["url"]
                )
                self.refresh()
            except (ValueError, KeyError) as e:
                messagebox.showerror("错误", str(e))
    
    def _delete_link(self) -> None:
        """Delete selected link."""
        link_id = self._get_selected_link_id()
        if not link_id:
            messagebox.showwarning("提示", "请先选择一个链接")
            return
        
        if messagebox.askyesno("确认", "确定要删除这个链接吗？"):
            try:
                self.link_manager.delete_link(link_id)
                self.refresh()
            except KeyError as e:
                messagebox.showerror("错误", str(e))
    
    def _open_link(self) -> None:
        """Open selected link in browser."""
        link_id = self._get_selected_link_id()
        if not link_id:
            messagebox.showwarning("提示", "请先选择一个链接")
            return
        
        try:
            self.link_manager.open_link(link_id)
        except KeyError as e:
            messagebox.showerror("错误", str(e))


class LinkDialog:
    """Dialog for adding/editing links."""
    
    def __init__(self, parent, title: str, name: str = "", url: str = ""):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Name
        ttk.Label(self.dialog, text="名称:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.name_entry = ttk.Entry(self.dialog, width=40)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)
        self.name_entry.insert(0, name)
        
        # URL
        ttk.Label(self.dialog, text="URL:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.url_entry = ttk.Entry(self.dialog, width=40)
        self.url_entry.grid(row=1, column=1, padx=10, pady=10)
        self.url_entry.insert(0, url or "https://")
        
        # Buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="确定", command=self._on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self._on_cancel).pack(side=tk.LEFT)
        
        self.dialog.wait_window()
    
    def _on_ok(self) -> None:
        """Handle OK button."""
        name = self.name_entry.get().strip()
        url = self.url_entry.get().strip()
        
        if not name:
            messagebox.showerror("错误", "名称不能为空")
            return
        
        if not LinkManager.validate_url(url):
            messagebox.showerror("错误", "URL格式不正确，需要以 http:// 或 https:// 开头")
            return
        
        self.result = {"name": name, "url": url}
        self.dialog.destroy()
    
    def _on_cancel(self) -> None:
        """Handle Cancel button."""
        self.dialog.destroy()
