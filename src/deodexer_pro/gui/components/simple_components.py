"""
Simplified GUI components for initial testing
"""

import tkinter as tk
from tkinter import ttk


class JobManagerFrame(ttk.Frame):
    """Simplified Job Manager Frame"""
    
    def __init__(self, parent, engine, db_manager):
        super().__init__(parent)
        self.engine = engine
        self.db_manager = db_manager
        
        label = ttk.Label(self, text="Job Manager - Coming Soon", style='Title.TLabel')
        label.pack(expand=True)
    
    def create_new_job(self):
        pass
    
    def load_job_config(self, config):
        pass
    
    def get_current_config(self):
        return {}
    
    def refresh(self):
        pass


class ProgressMonitorFrame(ttk.Frame):
    """Simplified Progress Monitor Frame"""
    
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        
        label = ttk.Label(self, text="Progress Monitor - Coming Soon", style='Title.TLabel')
        label.pack(expand=True)
    
    def refresh(self):
        pass


class SettingsFrame(ttk.Frame):
    """Simplified Settings Frame"""
    
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        
        label = ttk.Label(self, text="Settings - Coming Soon", style='Title.TLabel')
        label.pack(expand=True)
    
    def refresh_settings(self):
        pass
    
    def save_settings(self):
        pass


class FileBrowserFrame(ttk.Frame):
    """Simplified File Browser Frame"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        label = ttk.Label(self, text="File Browser - Coming Soon", style='Title.TLabel')
        label.pack(expand=True)