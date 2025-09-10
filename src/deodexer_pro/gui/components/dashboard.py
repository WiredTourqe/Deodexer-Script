"""
Simplified Dashboard component for displaying system overview
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any
import threading
import time

from ...database.manager import DatabaseManager
from ...core.logger import logger


class DashboardFrame(ttk.Frame):
    """Simplified dashboard frame showing system overview"""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        super().__init__(parent)
        self.db_manager = db_manager
        self._setup_dashboard()
        self._start_auto_refresh()
    
    def _setup_dashboard(self) -> None:
        """Setup dashboard layout and components"""
        # Title
        title_label = ttk.Label(self, text="System Dashboard", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Create main container
        main_container = tk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Statistics overview section
        self._create_statistics_section(main_container)
        
        # Recent activity section
        self._create_activity_section(main_container)
        
        # Initial data load
        self.refresh()
    
    def _create_statistics_section(self, parent) -> None:
        """Create statistics overview section"""
        stats_frame = ttk.LabelFrame(parent, text="System Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create grid of statistics cards
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # Statistics variables
        self.total_jobs_var = tk.StringVar(value="0")
        self.completed_jobs_var = tk.StringVar(value="0")
        self.success_rate_var = tk.StringVar(value="0%")
        self.total_files_var = tk.StringVar(value="0")
        
        # Create statistics cards
        self._create_stat_card(stats_grid, "Total Jobs", self.total_jobs_var, 0, 0)
        self._create_stat_card(stats_grid, "Completed Jobs", self.completed_jobs_var, 0, 1)
        self._create_stat_card(stats_grid, "Success Rate", self.success_rate_var, 1, 0)
        self._create_stat_card(stats_grid, "Files Processed", self.total_files_var, 1, 1)
    
    def _create_stat_card(self, parent, title: str, value_var: tk.StringVar, row: int, col: int) -> None:
        """Create individual statistics card"""
        card_frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=1)
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        parent.grid_columnconfigure(col, weight=1)
        
        title_label = ttk.Label(card_frame, text=title, style='Heading.TLabel')
        title_label.pack(pady=(10, 5))
        
        value_label = ttk.Label(card_frame, textvariable=value_var, font=('Arial', 16, 'bold'))
        value_label.pack(pady=(0, 10))
    
    def _create_activity_section(self, parent) -> None:
        """Create recent activity section"""
        activity_frame = ttk.LabelFrame(parent, text="Recent Activity", padding=10)
        activity_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for activity log
        columns = ('Time', 'Event', 'Status', 'Details')
        self.activity_tree = ttk.Treeview(activity_frame, columns=columns, show='headings', height=10)
        
        # Configure columns
        self.activity_tree.heading('Time', text='Time')
        self.activity_tree.heading('Event', text='Event')
        self.activity_tree.heading('Status', text='Status')
        self.activity_tree.heading('Details', text='Details')
        
        self.activity_tree.column('Time', width=120, minwidth=100)
        self.activity_tree.column('Event', width=150, minwidth=100)
        self.activity_tree.column('Status', width=100, minwidth=80)
        self.activity_tree.column('Details', width=300, minwidth=200)
        
        # Add scrollbar
        activity_scrollbar = ttk.Scrollbar(activity_frame, orient=tk.VERTICAL, command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=activity_scrollbar.set)
        
        # Pack components
        self.activity_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        activity_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _start_auto_refresh(self) -> None:
        """Start automatic dashboard refresh"""
        self.auto_refresh_active = True
        self.refresh_thread = threading.Thread(target=self._auto_refresh_loop, daemon=True)
        self.refresh_thread.start()
    
    def _auto_refresh_loop(self) -> None:
        """Auto refresh loop running in background"""
        while self.auto_refresh_active:
            try:
                self.after(0, self.refresh)  # Schedule refresh on main thread
                time.sleep(30)  # Refresh every 30 seconds
            except Exception as e:
                logger.error("Dashboard auto-refresh error", error=str(e))
                time.sleep(60)  # Wait longer on error
    
    def refresh(self) -> None:
        """Refresh dashboard data"""
        try:
            self._update_statistics()
            self._update_activity()
        except Exception as e:
            logger.error("Dashboard refresh failed", error=str(e))
    
    def _update_statistics(self) -> None:
        """Update statistics cards"""
        try:
            stats = self.db_manager.get_job_statistics()
            
            self.total_jobs_var.set(str(stats.get('total_jobs', 0)))
            self.completed_jobs_var.set(str(stats.get('completed_jobs', 0)))
            self.success_rate_var.set(f"{stats.get('success_rate', 0):.1f}%")
            self.total_files_var.set(str(stats.get('total_files_processed', 0)))
            
        except Exception as e:
            logger.error("Failed to update statistics", error=str(e))
    
    def _update_activity(self) -> None:
        """Update recent activity log"""
        try:
            # Clear existing items
            for item in self.activity_tree.get_children():
                self.activity_tree.delete(item)
            
            # Get recent jobs
            recent_jobs = self.db_manager.get_jobs(limit=10)
            
            for job in recent_jobs:
                time_str = job.created_at.strftime("%H:%M:%S") if job.created_at else "N/A"
                event = f"Job: {job.job_name}"
                status = job.status.title()
                details = f"{job.processed_files}/{job.total_files} files"
                
                # Color coding based on status
                tags = []
                if job.status == 'completed':
                    tags = ['success']
                elif job.status == 'failed':
                    tags = ['error']
                elif job.status == 'running':
                    tags = ['running']
                
                self.activity_tree.insert('', 'end', values=(time_str, event, status, details), tags=tags)
            
            # Configure tag colors
            self.activity_tree.tag_configure('success', foreground='green')
            self.activity_tree.tag_configure('error', foreground='red')
            self.activity_tree.tag_configure('running', foreground='blue')
            
        except Exception as e:
            logger.error("Failed to update activity log", error=str(e))
    
    def stop_auto_refresh(self) -> None:
        """Stop automatic refresh"""
        self.auto_refresh_active = False