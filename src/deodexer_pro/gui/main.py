"""
Main GUI Application for Deodexer Pro
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import asyncio
import threading
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from datetime import datetime

from ..core.config import config
from ..core.logger import logger
from ..core.deodexer import DeodexerEngine, DeodexingResult
from ..database.manager import DatabaseManager
from .components.job_manager import JobManagerFrame
from .components.progress_monitor import ProgressMonitorFrame
from .components.settings_manager import SettingsFrame
from .components.dashboard import DashboardFrame
from .components.file_browser import FileBrowserFrame


class DeodexerProGUI:
    """Main GUI application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.engine = DeodexerEngine()
        self.db_manager = DatabaseManager()
        self.current_job = None
        self._setup_gui()
        self._setup_event_loop()
        
    def _setup_gui(self) -> None:
        """Setup the main GUI interface"""
        # Configure main window
        self.root.title(f"{config.get('app.name', 'Deodexer Pro')} v{config.get('app.version', '2.0.0')}")
        self.root.geometry(f"{config.get('gui.window.width', 1200)}x{config.get('gui.window.height', 800)}")
        self.root.minsize(800, 600)
        
        # Center window on screen
        if config.get('gui.window.center_on_start', True):
            self._center_window()
        
        # Configure style
        self._setup_theme()
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tab frames
        self._create_tabs()
        
        # Create status bar
        self._create_status_bar()
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        logger.info("GUI initialized successfully")
    
    def _center_window(self) -> None:
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _setup_theme(self) -> None:
        """Setup GUI theme and styling"""
        style = ttk.Style()
        
        # Try to use modern theme
        available_themes = style.theme_names()
        preferred_themes = ['vista', 'clam', 'alt', 'default']
        
        selected_theme = 'default'
        for theme in preferred_themes:
            if theme in available_themes:
                selected_theme = theme
                break
        
        style.theme_use(selected_theme)
        
        # Custom styling
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
        
        # Configure colors based on theme preference
        theme_pref = config.get('gui.theme', 'light')
        if theme_pref == 'dark':
            # Configure dark theme colors
            style.configure('TFrame', background='#2d2d2d')
            style.configure('TLabel', background='#2d2d2d', foreground='white')
            style.configure('TNotebook', background='#2d2d2d')
            style.configure('TNotebook.Tab', background='#404040', foreground='white')
    
    def _create_menu_bar(self) -> None:
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Job", command=self._new_job, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Job", command=self._open_job, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Job", command=self._save_job, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Import Configuration", command=self._import_config)
        file_menu.add_command(label="Export Configuration", command=self._export_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing, accelerator="Ctrl+Q")
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Batch Processor", command=self._open_batch_processor)
        tools_menu.add_command(label="File Analyzer", command=self._open_file_analyzer)
        tools_menu.add_command(label="Performance Monitor", command=self._open_performance_monitor)
        tools_menu.add_separator()
        tools_menu.add_command(label="Database Maintenance", command=self._open_db_maintenance)
        tools_menu.add_command(label="Clear Cache", command=self._clear_cache)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh", command=self._refresh_view, accelerator="F5")
        view_menu.add_command(label="Toggle Fullscreen", command=self._toggle_fullscreen, accelerator="F11")
        view_menu.add_separator()
        view_menu.add_command(label="Show Logs", command=self._show_logs)
        view_menu.add_command(label="Show Statistics", command=self._show_statistics)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self._show_documentation)
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)
        help_menu.add_command(label="Check for Updates", command=self._check_updates)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self._new_job())
        self.root.bind('<Control-o>', lambda e: self._open_job())
        self.root.bind('<Control-s>', lambda e: self._save_job())
        self.root.bind('<Control-q>', lambda e: self._on_closing())
        self.root.bind('<F5>', lambda e: self._refresh_view())
        self.root.bind('<F11>', lambda e: self._toggle_fullscreen())
    
    def _create_tabs(self) -> None:
        """Create main application tabs"""
        # Dashboard tab
        self.dashboard_frame = DashboardFrame(self.notebook, self.db_manager)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        # Job Manager tab
        self.job_manager_frame = JobManagerFrame(self.notebook, self.engine, self.db_manager)
        self.notebook.add(self.job_manager_frame, text="Job Manager")
        
        # File Browser tab
        self.file_browser_frame = FileBrowserFrame(self.notebook)
        self.notebook.add(self.file_browser_frame, text="File Browser")
        
        # Progress Monitor tab
        self.progress_monitor_frame = ProgressMonitorFrame(self.notebook, self.db_manager)
        self.notebook.add(self.progress_monitor_frame, text="Progress Monitor")
        
        # Settings tab
        self.settings_frame = SettingsFrame(self.notebook, config)
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Set initial tab
        self.notebook.select(0)
    
    def _create_status_bar(self) -> None:
        """Create status bar at bottom of window"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_label = ttk.Label(
            self.status_frame, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)
        
        # Progress bar (hidden by default)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.status_frame,
            variable=self.progress_var,
            maximum=100
        )
        
        # System info labels
        self.system_info_frame = ttk.Frame(self.status_frame)
        self.system_info_frame.pack(side=tk.RIGHT, padx=2, pady=2)
        
        self.jobs_label = ttk.Label(self.system_info_frame, text="Jobs: 0")
        self.jobs_label.pack(side=tk.RIGHT, padx=5)
        
        self.memory_label = ttk.Label(self.system_info_frame, text="Memory: 0%")
        self.memory_label.pack(side=tk.RIGHT, padx=5)
        
        # Update system info periodically
        self._update_system_info()
    
    def _setup_event_loop(self) -> None:
        """Setup asyncio event loop for async operations"""
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.loop_thread.start()
    
    def _run_event_loop(self) -> None:
        """Run asyncio event loop in separate thread"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def _update_system_info(self) -> None:
        """Update system information in status bar"""
        try:
            # Get job statistics
            stats = self.db_manager.get_job_statistics()
            active_jobs = stats.get('running_jobs', 0)
            self.jobs_label.config(text=f"Jobs: {active_jobs}")
            
            # Get memory usage (simplified)
            import psutil
            memory_percent = psutil.virtual_memory().percent
            self.memory_label.config(text=f"Memory: {memory_percent:.1f}%")
            
        except Exception as e:
            logger.error("Failed to update system info", error=str(e))
        
        # Schedule next update
        self.root.after(5000, self._update_system_info)  # Update every 5 seconds
    
    def update_status(self, message: str, progress: Optional[float] = None) -> None:
        """Update status bar message and optional progress"""
        self.status_var.set(message)
        
        if progress is not None:
            self.progress_var.set(progress)
            if not self.progress_bar.winfo_viewable():
                self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=2)
        else:
            if self.progress_bar.winfo_viewable():
                self.progress_bar.pack_forget()
        
        self.root.update_idletasks()
    
    def show_error(self, title: str, message: str) -> None:
        """Show error dialog"""
        messagebox.showerror(title, message)
        logger.error("GUI Error", title=title, message=message)
    
    def show_warning(self, title: str, message: str) -> None:
        """Show warning dialog"""
        messagebox.showwarning(title, message)
        logger.warning("GUI Warning", title=title, message=message)
    
    def show_info(self, title: str, message: str) -> None:
        """Show info dialog"""
        messagebox.showinfo(title, message)
        logger.info("GUI Info", title=title, message=message)
    
    # Menu command implementations
    def _new_job(self) -> None:
        """Create new deodexing job"""
        self.job_manager_frame.create_new_job()
        self.notebook.select(1)  # Switch to Job Manager tab
    
    def _open_job(self) -> None:
        """Open existing job"""
        # Implementation for opening saved job configurations
        file_path = filedialog.askopenfilename(
            title="Open Job Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    job_config = json.load(f)
                self.job_manager_frame.load_job_config(job_config)
                self.update_status(f"Loaded job configuration: {Path(file_path).name}")
            except Exception as e:
                self.show_error("Error", f"Failed to load job configuration: {str(e)}")
    
    def _save_job(self) -> None:
        """Save current job configuration"""
        config_data = self.job_manager_frame.get_current_config()
        if not config_data:
            self.show_warning("Warning", "No job configuration to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Job Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
                self.update_status(f"Saved job configuration: {Path(file_path).name}")
            except Exception as e:
                self.show_error("Error", f"Failed to save job configuration: {str(e)}")
    
    def _import_config(self) -> None:
        """Import application configuration"""
        file_path = filedialog.askopenfilename(
            title="Import Configuration",
            filetypes=[("YAML files", "*.yaml"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                if file_path.endswith('.yaml'):
                    import yaml
                    with open(file_path, 'r') as f:
                        config_data = yaml.safe_load(f)
                else:
                    with open(file_path, 'r') as f:
                        config_data = json.load(f)
                
                config.update(config_data)
                self.settings_frame.refresh_settings()
                self.update_status("Configuration imported successfully")
            except Exception as e:
                self.show_error("Error", f"Failed to import configuration: {str(e)}")
    
    def _export_config(self) -> None:
        """Export current configuration"""
        file_path = filedialog.asksaveasfilename(
            title="Export Configuration",
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                config_data = config.to_dict()
                if file_path.endswith('.yaml'):
                    import yaml
                    with open(file_path, 'w') as f:
                        yaml.dump(config_data, f, default_flow_style=False, indent=2)
                else:
                    with open(file_path, 'w') as f:
                        json.dump(config_data, f, indent=2)
                
                self.update_status("Configuration exported successfully")
            except Exception as e:
                self.show_error("Error", f"Failed to export configuration: {str(e)}")
    
    def _refresh_view(self) -> None:
        """Refresh current view"""
        current_tab = self.notebook.select()
        tab_index = self.notebook.index(current_tab)
        
        if tab_index == 0:  # Dashboard
            self.dashboard_frame.refresh()
        elif tab_index == 1:  # Job Manager
            self.job_manager_frame.refresh()
        elif tab_index == 3:  # Progress Monitor
            self.progress_monitor_frame.refresh()
        
        self.update_status("View refreshed")
    
    def _toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
    
    def _show_about(self) -> None:
        """Show about dialog"""
        about_text = f"""
{config.get('app.name', 'Deodexer Pro')} v{config.get('app.version', '2.0.0')}

Advanced Android Deodexer with GUI and comprehensive analysis tools.

Features:
• Modern GUI interface
• Batch processing with progress tracking
• Database integration for history tracking
• Advanced file analysis and optimization
• Real-time performance monitoring
• Comprehensive reporting and export capabilities

Developed by: {config.get('app.author', 'WiredTourqe')}
        """
        messagebox.showinfo("About", about_text.strip())
    
    def _on_closing(self) -> None:
        """Handle application closing"""
        try:
            # Save current settings
            self.settings_frame.save_settings()
            
            # Close database connections
            if hasattr(self, 'db_manager'):
                # Cleanup any running operations
                pass
            
            # Stop event loop
            if hasattr(self, 'loop'):
                self.loop.call_soon_threadsafe(self.loop.stop)
            
            logger.info("Application closing")
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            logger.error("Error during application shutdown", error=str(e))
            self.root.quit()
    
    # Placeholder implementations for menu commands
    def _open_batch_processor(self): pass
    def _open_file_analyzer(self): pass
    def _open_performance_monitor(self): pass
    def _open_db_maintenance(self): pass
    def _clear_cache(self): pass
    def _show_logs(self): pass
    def _show_statistics(self): pass
    def _show_documentation(self): pass
    def _show_shortcuts(self): pass
    def _check_updates(self): pass
    
    def run(self) -> None:
        """Start the GUI application"""
        try:
            logger.info("Starting GUI application")
            self.root.mainloop()
        except Exception as e:
            logger.error("GUI application error", error=str(e))
            raise


def main():
    """Main entry point for GUI application"""
    try:
        app = DeodexerProGUI()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        logger.error("Application startup failed", error=str(e))


if __name__ == "__main__":
    main()