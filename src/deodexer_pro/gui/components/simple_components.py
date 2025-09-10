"""
Simplified GUI components for initial testing
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import asyncio
import threading
import time
from pathlib import Path


class JobManagerFrame(ttk.Frame):
    """Functional Job Manager Frame for deodexing operations"""
    
    def __init__(self, parent, engine, db_manager):
        super().__init__(parent)
        self.engine = engine
        self.db_manager = db_manager
        self.current_job = None
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the job manager interface"""
        # Main container with scrolling
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Deodexing Job Manager", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Configuration frame
        config_frame = ttk.LabelFrame(main_frame, text="Deodexing Configuration", padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Input directory selection
        input_frame = ttk.Frame(config_frame)
        input_frame.pack(fill=tk.X, pady=5)
        ttk.Label(input_frame, text="Input Directory (ODEX files):").pack(anchor=tk.W)
        input_path_frame = ttk.Frame(input_frame)
        input_path_frame.pack(fill=tk.X, pady=2)
        self.input_path_var = tk.StringVar()
        self.input_path_entry = ttk.Entry(input_path_frame, textvariable=self.input_path_var)
        self.input_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(input_path_frame, text="Browse", 
                  command=self._browse_input_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Framework directory selection
        framework_frame = ttk.Frame(config_frame)
        framework_frame.pack(fill=tk.X, pady=5)
        ttk.Label(framework_frame, text="Framework Directory:").pack(anchor=tk.W)
        framework_path_frame = ttk.Frame(framework_frame)
        framework_path_frame.pack(fill=tk.X, pady=2)
        self.framework_path_var = tk.StringVar()
        self.framework_path_entry = ttk.Entry(framework_path_frame, textvariable=self.framework_path_var)
        self.framework_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(framework_path_frame, text="Browse", 
                  command=self._browse_framework_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Output directory selection
        output_frame = ttk.Frame(config_frame)
        output_frame.pack(fill=tk.X, pady=5)
        ttk.Label(output_frame, text="Output Directory:").pack(anchor=tk.W)
        output_path_frame = ttk.Frame(output_frame)
        output_path_frame.pack(fill=tk.X, pady=2)
        self.output_path_var = tk.StringVar()
        self.output_path_entry = ttk.Entry(output_path_frame, textvariable=self.output_path_var)
        self.output_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_path_frame, text="Browse", 
                  command=self._browse_output_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Baksmali JAR selection
        baksmali_frame = ttk.Frame(config_frame)
        baksmali_frame.pack(fill=tk.X, pady=5)
        ttk.Label(baksmali_frame, text="Baksmali JAR:").pack(anchor=tk.W)
        baksmali_path_frame = ttk.Frame(baksmali_frame)
        baksmali_path_frame.pack(fill=tk.X, pady=2)
        self.baksmali_path_var = tk.StringVar()
        self.baksmali_path_entry = ttk.Entry(baksmali_path_frame, textvariable=self.baksmali_path_var)
        self.baksmali_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(baksmali_path_frame, text="Browse", 
                  command=self._browse_baksmali_jar).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(baksmali_path_frame, text="Auto-detect", 
                  command=self._auto_detect_baksmali).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Advanced options frame
        advanced_frame = ttk.LabelFrame(config_frame, text="Advanced Options", padding=5)
        advanced_frame.pack(fill=tk.X, pady=(10, 0))
        
        # API Level
        api_frame = ttk.Frame(advanced_frame)
        api_frame.pack(fill=tk.X, pady=2)
        ttk.Label(api_frame, text="API Level:").pack(side=tk.LEFT)
        self.api_level_var = tk.StringVar(value="29")
        api_spinbox = ttk.Spinbox(api_frame, from_=1, to=34, width=10, textvariable=self.api_level_var)
        api_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        # Max workers
        workers_frame = ttk.Frame(advanced_frame)
        workers_frame.pack(fill=tk.X, pady=2)
        ttk.Label(workers_frame, text="Max Workers:").pack(side=tk.LEFT)
        self.max_workers_var = tk.StringVar(value="4")
        workers_spinbox = ttk.Spinbox(workers_frame, from_=1, to=16, width=10, textvariable=self.max_workers_var)
        workers_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(control_frame, text="Start Deodexing", 
                                      command=self._start_deodexing, style='Accent.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="Stop", 
                                     command=self._stop_deodexing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.validate_button = ttk.Button(control_frame, text="Validate Setup", 
                                         command=self._validate_setup)
        self.validate_button.pack(side=tk.LEFT, padx=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.pack(anchor=tk.W)
        
        # Results text area
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(results_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(text_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Auto-detect systems on startup
        self._auto_detect_environment()
    
    def _browse_input_dir(self):
        """Browse for input directory"""
        directory = filedialog.askdirectory(title="Select Input Directory with ODEX files")
        if directory:
            self.input_path_var.set(directory)
            self._log_message(f"Input directory selected: {directory}")
    
    def _browse_framework_dir(self):
        """Browse for framework directory"""
        directory = filedialog.askdirectory(title="Select Framework Directory")
        if directory:
            self.framework_path_var.set(directory)
            self._log_message(f"Framework directory selected: {directory}")
    
    def _browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_path_var.set(directory)
            self._log_message(f"Output directory selected: {directory}")
    
    def _browse_baksmali_jar(self):
        """Browse for baksmali JAR file"""
        jar_file = filedialog.askopenfilename(
            title="Select Baksmali JAR file",
            filetypes=[("JAR files", "*.jar"), ("All files", "*.*")]
        )
        if jar_file:
            self.baksmali_path_var.set(jar_file)
            self._log_message(f"Baksmali JAR selected: {jar_file}")
    
    def _auto_detect_baksmali(self):
        """Auto-detect baksmali JAR"""
        # Try to find baksmali JAR
        search_paths = [
            "./baksmali.jar",
            "tools/baksmali.jar",
            os.path.expanduser("~/tools/baksmali.jar"),
            "/usr/local/bin/baksmali.jar"
        ]
        
        for path in search_paths:
            if os.path.isfile(path):
                self.baksmali_path_var.set(os.path.abspath(path))
                self._log_message(f"Auto-detected baksmali JAR: {path}")
                return
        
        # If not found, suggest download
        response = messagebox.askyesno(
            "Baksmali Not Found", 
            "Baksmali JAR not found in standard locations.\n\n"
            "Would you like to download it automatically from:\n"
            "https://github.com/JesusFreke/smali/releases?\n\n"
            "Otherwise, please download and select it manually."
        )
        if response:
            self._download_baksmali()
        
    def _download_baksmali(self):
        """Download baksmali JAR automatically"""
        import requests
        import json
        
        try:
            self._log_message("Checking for latest baksmali release...")
            # Get latest release info from GitHub API
            response = requests.get("https://api.github.com/repos/JesusFreke/smali/releases/latest")
            if response.status_code == 200:
                release_data = response.json()
                
                # Find baksmali JAR asset
                baksmali_asset = None
                for asset in release_data.get('assets', []):
                    if 'baksmali' in asset['name'].lower() and asset['name'].endswith('.jar'):
                        baksmali_asset = asset
                        break
                
                if baksmali_asset:
                    # Download the file
                    download_url = baksmali_asset['browser_download_url']
                    filename = baksmali_asset['name']
                    
                    self._log_message(f"Downloading {filename}...")
                    
                    response = requests.get(download_url)
                    if response.status_code == 200:
                        # Save to tools directory
                        tools_dir = "tools"
                        os.makedirs(tools_dir, exist_ok=True)
                        jar_path = os.path.join(tools_dir, filename)
                        
                        with open(jar_path, 'wb') as f:
                            f.write(response.content)
                        
                        self.baksmali_path_var.set(os.path.abspath(jar_path))
                        self._log_message(f"Downloaded baksmali JAR: {jar_path}")
                    else:
                        raise Exception(f"Download failed: {response.status_code}")
                else:
                    raise Exception("No baksmali JAR found in latest release")
            else:
                raise Exception(f"GitHub API request failed: {response.status_code}")
                
        except Exception as e:
            self._log_message(f"Auto-download failed: {str(e)}")
            messagebox.showerror("Download Failed", 
                               f"Failed to download baksmali automatically:\n{str(e)}\n\n"
                               "Please download manually from:\n"
                               "https://github.com/JesusFreke/smali/releases")
    
    def _auto_detect_environment(self):
        """Auto-detect Java and other environment components"""
        self._log_message("Auto-detecting environment...")
        
        # Check Java
        try:
            import subprocess
            result = subprocess.run(["java", "-version"], capture_output=True, text=True)
            if result.returncode == 0:
                # Parse Java version from stderr (Java outputs version to stderr)
                version_info = result.stderr.split('\n')[0]
                self._log_message(f"✓ Java detected: {version_info}")
            else:
                self._log_message("✗ Java not found or not working")
        except Exception as e:
            self._log_message(f"✗ Java check failed: {str(e)}")
        
        # Check for baksmali
        if self.engine.baksmali_jar:
            self.baksmali_path_var.set(self.engine.baksmali_jar)
            self._log_message(f"✓ Baksmali JAR: {self.engine.baksmali_jar}")
        else:
            self._log_message("✗ Baksmali JAR not configured")
    
    def _validate_setup(self):
        """Validate current setup"""
        self._log_message("Validating setup...")
        
        errors = []
        warnings = []
        
        # Check input directory
        input_dir = self.input_path_var.get().strip()
        if not input_dir:
            errors.append("Input directory not selected")
        elif not os.path.isdir(input_dir):
            errors.append("Input directory does not exist")
        else:
            # Count ODEX files
            odex_count = sum(1 for root, dirs, files in os.walk(input_dir) 
                           for file in files if file.endswith('.odex'))
            if odex_count == 0:
                warnings.append("No ODEX files found in input directory")
            else:
                self._log_message(f"✓ Found {odex_count} ODEX files in input directory")
        
        # Check framework directory
        framework_dir = self.framework_path_var.get().strip()
        if not framework_dir:
            warnings.append("Framework directory not selected (may cause issues)")
        elif not os.path.isdir(framework_dir):
            errors.append("Framework directory does not exist")
        
        # Check output directory
        output_dir = self.output_path_var.get().strip()
        if not output_dir:
            errors.append("Output directory not selected")
        else:
            # Try to create if it doesn't exist
            try:
                os.makedirs(output_dir, exist_ok=True)
                self._log_message(f"✓ Output directory ready: {output_dir}")
            except Exception as e:
                errors.append(f"Cannot create output directory: {str(e)}")
        
        # Check baksmali JAR
        baksmali_jar = self.baksmali_path_var.get().strip()
        if not baksmali_jar:
            errors.append("Baksmali JAR not selected")
        elif not os.path.isfile(baksmali_jar):
            errors.append("Baksmali JAR file does not exist")
        else:
            self._log_message(f"✓ Baksmali JAR: {baksmali_jar}")
        
        # Display results
        if errors:
            error_msg = "Setup validation failed:\n" + "\n".join(f"• {error}" for error in errors)
            self._log_message(f"✗ Validation failed: {len(errors)} errors")
            messagebox.showerror("Validation Failed", error_msg)
        elif warnings:
            warning_msg = "Setup has warnings:\n" + "\n".join(f"• {warning}" for warning in warnings)
            self._log_message(f"⚠ Validation completed with warnings")
            messagebox.showwarning("Validation Warnings", warning_msg)
        else:
            self._log_message("✓ Setup validation passed!")
            messagebox.showinfo("Validation Passed", "All settings are valid. Ready to start deodexing!")
    
    def _start_deodexing(self):
        """Start the deodexing process"""
        # Validate first
        if not self._validate_inputs():
            return
        
        # Update UI state
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.status_var.set("Starting deodexing...")
        
        # Clear results
        self.results_text.delete(1.0, tk.END)
        
        # Start deodexing in separate thread
        self.deodex_thread = threading.Thread(target=self._run_deodexing, daemon=True)
        self.deodex_thread.start()
    
    def _validate_inputs(self):
        """Validate inputs before starting"""
        input_dir = self.input_path_var.get().strip()
        framework_dir = self.framework_path_var.get().strip()
        output_dir = self.output_path_var.get().strip()
        baksmali_jar = self.baksmali_path_var.get().strip()
        
        if not all([input_dir, output_dir, baksmali_jar]):
            messagebox.showerror("Missing Information", 
                               "Please fill in all required fields (Input, Output, Baksmali JAR)")
            return False
        
        if not os.path.isdir(input_dir):
            messagebox.showerror("Invalid Input", "Input directory does not exist")
            return False
        
        if not os.path.isfile(baksmali_jar):
            messagebox.showerror("Invalid Baksmali", "Baksmali JAR file does not exist")
            return False
        
        return True
    
    def _run_deodexing(self):
        """Run deodexing in background thread"""
        try:
            # Get parameters
            input_dir = self.input_path_var.get().strip()
            framework_dir = self.framework_path_var.get().strip() or None
            output_dir = self.output_path_var.get().strip()
            baksmali_jar = self.baksmali_path_var.get().strip()
            api_level = int(self.api_level_var.get())
            max_workers = int(self.max_workers_var.get())
            
            # Set baksmali JAR
            self.engine.set_baksmali_jar(baksmali_jar)
            
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run deodexing
            results = loop.run_until_complete(
                self.engine.deodex_batch_async(
                    input_dir=input_dir,
                    framework_dir=framework_dir,
                    output_dir=output_dir,
                    api_level=api_level,
                    max_workers=max_workers,
                    progress_callback=self._progress_callback
                )
            )
            
            # Generate report
            report = self.engine.generate_report(results)
            
            # Update UI with results
            self.master.after(0, self._deodexing_completed, report)
            
        except Exception as e:
            self.master.after(0, self._deodexing_failed, str(e))
        finally:
            loop.close()
    
    def _progress_callback(self, progress_info):
        """Handle progress updates from deodexing"""
        completed = progress_info['completed']
        total = progress_info['total']
        current_file = progress_info.get('current_file', '')
        
        # Update progress bar
        progress_percent = (completed / total * 100) if total > 0 else 0
        self.master.after(0, self._update_progress, progress_percent, completed, total, current_file)
    
    def _update_progress(self, percent, completed, total, current_file):
        """Update progress UI"""
        self.progress_var.set(percent)
        self.status_var.set(f"Processing {completed}/{total}: {os.path.basename(current_file)}")
        
        # Log progress
        if completed % 5 == 0 or completed == total:  # Log every 5 files
            self._log_message(f"Progress: {completed}/{total} files completed ({percent:.1f}%)")
    
    def _deodexing_completed(self, report):
        """Handle successful completion"""
        # Update UI state
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_var.set(100)
        
        # Display results
        summary = report['summary']
        self.status_var.set(f"Completed: {summary['successful']}/{summary['total_files']} successful")
        
        # Log detailed results
        self._log_message(f"\n=== DEODEXING COMPLETED ===")
        self._log_message(f"Total files: {summary['total_files']}")
        self._log_message(f"Successful: {summary['successful']}")
        self._log_message(f"Failed: {summary['failed']}")
        self._log_message(f"Success rate: {summary['success_rate']:.1f}%")
        self._log_message(f"Total time: {summary['total_duration']:.2f} seconds")
        
        if summary['failed'] > 0:
            self._log_message(f"\nFailed files:")
            for error in report['errors']:
                self._log_message(f"  • {error['file']}: {error['error']}")
        
        # Export report
        try:
            report_file = self.engine.export_report(report['results'], 'json')
            self._log_message(f"\nReport saved: {report_file}")
        except Exception as e:
            self._log_message(f"Failed to save report: {str(e)}")
        
        # Show completion dialog
        if summary['failed'] == 0:
            messagebox.showinfo("Success", 
                              f"Deodexing completed successfully!\n\n"
                              f"Processed {summary['total_files']} files in {summary['total_duration']:.1f} seconds")
        else:
            messagebox.showwarning("Completed with Errors", 
                                 f"Deodexing completed with {summary['failed']} errors out of {summary['total_files']} files.\n\n"
                                 f"Check the results panel for details.")
    
    def _deodexing_failed(self, error_message):
        """Handle deodexing failure"""
        # Update UI state
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Failed")
        
        # Log error
        self._log_message(f"\n=== DEODEXING FAILED ===")
        self._log_message(f"Error: {error_message}")
        
        # Show error dialog
        messagebox.showerror("Deodexing Failed", f"Deodexing failed with error:\n\n{error_message}")
    
    def _stop_deodexing(self):
        """Stop the deodexing process"""
        # This is a simplified stop - in a real implementation you'd need proper cancellation
        self.status_var.set("Stopping...")
        self._log_message("Stop requested...")
        
        # Reset UI state
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
    def _log_message(self, message):
        """Log message to results text area"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.results_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.results_text.see(tk.END)
        self.results_text.update()
    
    def create_new_job(self):
        """Create new job (clear all fields)"""
        self.input_path_var.set("")
        self.framework_path_var.set("")
        self.output_path_var.set("")
        self.baksmali_path_var.set("")
        self.api_level_var.set("29")
        self.max_workers_var.set("4")
        self.results_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_var.set("Ready")
        self._log_message("New job created")
    
    def load_job_config(self, config):
        """Load job configuration"""
        self.input_path_var.set(config.get('input_dir', ''))
        self.framework_path_var.set(config.get('framework_dir', ''))
        self.output_path_var.set(config.get('output_dir', ''))
        self.baksmali_path_var.set(config.get('baksmali_jar', ''))
        self.api_level_var.set(str(config.get('api_level', 29)))
        self.max_workers_var.set(str(config.get('max_workers', 4)))
        self._log_message("Job configuration loaded")
    
    def get_current_config(self):
        """Get current configuration"""
        return {
            'input_dir': self.input_path_var.get(),
            'framework_dir': self.framework_path_var.get(),
            'output_dir': self.output_path_var.get(),
            'baksmali_jar': self.baksmali_path_var.get(),
            'api_level': int(self.api_level_var.get()),
            'max_workers': int(self.max_workers_var.get())
        }
    
    def refresh(self):
        """Refresh the view"""
        self._auto_detect_environment()


class ProgressMonitorFrame(ttk.Frame):
    """Progress Monitor Frame for tracking deodexing jobs"""
    
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup progress monitoring interface"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Progress Monitor", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Active jobs frame
        active_frame = ttk.LabelFrame(main_frame, text="Active Jobs", padding=10)
        active_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Treeview for active jobs
        columns = ('ID', 'Name', 'Status', 'Progress', 'Started')
        self.active_tree = ttk.Treeview(active_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.active_tree.heading(col, text=col)
            self.active_tree.column(col, width=100)
        
        scrollbar_active = ttk.Scrollbar(active_frame, orient=tk.VERTICAL, command=self.active_tree.yview)
        self.active_tree.configure(yscrollcommand=scrollbar_active.set)
        
        self.active_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_active.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Job history frame
        history_frame = ttk.LabelFrame(main_frame, text="Job History", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Treeview for job history
        history_columns = ('ID', 'Name', 'Status', 'Files', 'Success Rate', 'Duration', 'Completed')
        self.history_tree = ttk.Treeview(history_frame, columns=history_columns, show='headings', height=10)
        
        for col in history_columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        scrollbar_history = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar_history.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_history.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        button_frame = ttk.Frame(history_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Refresh", command=self.refresh).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear History", command=self._clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Report", command=self._export_history).pack(side=tk.LEFT, padx=5)
        
        # Initial refresh
        self.refresh()
    
    def refresh(self):
        """Refresh the progress monitor view"""
        # Clear existing items
        for item in self.active_tree.get_children():
            self.active_tree.delete(item)
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add sample data (in real implementation, get from database)
        sample_active = [
            ("1", "System Apps", "Running", "45%", "14:23:15"),
            ("2", "User Apps", "Queued", "0%", "Not started")
        ]
        
        for job in sample_active:
            self.active_tree.insert('', tk.END, values=job)
        
        sample_history = [
            ("003", "Framework", "Completed", "156", "98.7%", "2m 34s", "14:20:12"),
            ("002", "Boot Apps", "Completed", "87", "100%", "1m 12s", "14:15:45"),
            ("001", "Test Run", "Failed", "23", "45.2%", "0m 45s", "14:10:30")
        ]
        
        for job in sample_history:
            self.history_tree.insert('', tk.END, values=job)
    
    def _clear_history(self):
        """Clear job history"""
        if messagebox.askyesno("Clear History", "Are you sure you want to clear the job history?"):
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
    
    def _export_history(self):
        """Export job history"""
        messagebox.showinfo("Export", "Export functionality would save job history to CSV/JSON file")


class FileBrowserFrame(ttk.Frame):
    """File Browser Frame for exploring ODEX files and results"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup file browser interface"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="File Browser", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Path frame
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(path_frame, text="Current Path:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value=os.getcwd())
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, state='readonly')
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        ttk.Button(path_frame, text="Browse", command=self._browse_path).pack(side=tk.RIGHT, padx=(5, 0))
        
        # File tree frame
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # File tree
        self.file_tree = ttk.Treeview(tree_frame, show='tree headings')
        self.file_tree.heading('#0', text='Name')
        self.file_tree.column('#0', width=300)
        
        # Configure columns
        self.file_tree['columns'] = ('Size', 'Type', 'Modified')
        self.file_tree.heading('Size', text='Size')
        self.file_tree.heading('Type', text='Type')
        self.file_tree.heading('Modified', text='Modified')
        
        self.file_tree.column('Size', width=80)
        self.file_tree.column('Type', width=100)
        self.file_tree.column('Modified', width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack tree and scrollbars
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Info panel
        info_frame = ttk.LabelFrame(main_frame, text="File Information", padding=10)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.info_text = tk.Text(info_frame, height=4, wrap=tk.WORD)
        info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.file_tree.bind('<Double-1>', self._on_item_double_click)
        self.file_tree.bind('<<TreeviewSelect>>', self._on_item_select)
        
        # Initial load
        self._load_directory(self.path_var.get())
    
    def _browse_path(self):
        """Browse for a directory"""
        directory = filedialog.askdirectory(title="Select Directory to Browse")
        if directory:
            self.path_var.set(directory)
            self._load_directory(directory)
    
    def _load_directory(self, path):
        """Load directory contents into tree"""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        try:
            # Add parent directory item if not root
            if os.path.dirname(path) != path:
                self.file_tree.insert('', 0, text='..', values=('', 'Directory', ''), tags=('parent',))
            
            # List directory contents
            if os.path.isdir(path):
                items = []
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    try:
                        stat = os.stat(item_path)
                        if os.path.isdir(item_path):
                            size = ''
                            file_type = 'Directory'
                        else:
                            size = self._format_size(stat.st_size)
                            file_type = self._get_file_type(item)
                        
                        modified = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
                        items.append((item, size, file_type, modified, os.path.isdir(item_path)))
                    except (OSError, IOError):
                        # Skip inaccessible items
                        continue
                
                # Sort: directories first, then files
                items.sort(key=lambda x: (not x[4], x[0].lower()))
                
                # Insert items
                for item, size, file_type, modified, is_dir in items:
                    tags = ('directory',) if is_dir else ('file',)
                    if item.endswith('.odex'):
                        tags = tags + ('odex',)
                    
                    self.file_tree.insert('', tk.END, text=item, values=(size, file_type, modified), tags=tags)
                
                # Configure tag colors
                self.file_tree.tag_configure('directory', foreground='blue')
                self.file_tree.tag_configure('odex', foreground='red', font=('TkDefaultFont', 9, 'bold'))
                
        except Exception as e:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Error loading directory: {str(e)}")
    
    def _format_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def _get_file_type(self, filename):
        """Get file type based on extension"""
        ext = os.path.splitext(filename)[1].lower()
        type_map = {
            '.odex': 'ODEX File',
            '.apk': 'Android Package',
            '.jar': 'Java Archive',
            '.dex': 'Dalvik Executable',
            '.smali': 'Smali Source',
            '.xml': 'XML Document',
            '.txt': 'Text File',
            '.log': 'Log File',
            '.json': 'JSON Data',
            '.csv': 'CSV Data'
        }
        return type_map.get(ext, 'File')
    
    def _on_item_double_click(self, event):
        """Handle double-click on tree item"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            item_text = self.file_tree.item(item, 'text')
            
            if item_text == '..':
                # Go to parent directory
                current_path = self.path_var.get()
                parent_path = os.path.dirname(current_path)
                self.path_var.set(parent_path)
                self._load_directory(parent_path)
            else:
                # Navigate into directory or show file info
                current_path = self.path_var.get()
                item_path = os.path.join(current_path, item_text)
                
                if os.path.isdir(item_path):
                    self.path_var.set(item_path)
                    self._load_directory(item_path)
    
    def _on_item_select(self, event):
        """Handle item selection"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            item_text = self.file_tree.item(item, 'text')
            
            if item_text != '..':
                current_path = self.path_var.get()
                item_path = os.path.join(current_path, item_text)
                
                # Show file information
                self.info_text.delete(1.0, tk.END)
                try:
                    if os.path.isfile(item_path):
                        stat = os.stat(item_path)
                        info = f"Path: {item_path}\n"
                        info += f"Size: {self._format_size(stat.st_size)}\n"
                        info += f"Modified: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))}\n"
                        
                        if item_text.endswith('.odex'):
                            info += "\n*** ODEX FILE ***\nThis file can be deodexed using the Job Manager."
                        
                        self.info_text.insert(tk.END, info)
                    elif os.path.isdir(item_path):
                        try:
                            item_count = len(os.listdir(item_path))
                            odex_count = sum(1 for f in os.listdir(item_path) if f.endswith('.odex'))
                            info = f"Directory: {item_path}\n"
                            info += f"Items: {item_count}\n"
                            if odex_count > 0:
                                info += f"ODEX files: {odex_count}"
                            self.info_text.insert(tk.END, info)
                        except PermissionError:
                            self.info_text.insert(tk.END, "Permission denied")
                except Exception as e:
                    self.info_text.insert(tk.END, f"Error: {str(e)}")


class SettingsFrame(ttk.Frame):
    """Settings Frame for application configuration"""
    
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup settings interface"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Application Settings", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Create notebook for settings categories
        settings_notebook = ttk.Notebook(main_frame)
        settings_notebook.pack(fill=tk.BOTH, expand=True)
        
        # General settings tab
        general_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(general_frame, text="General")
        self._create_general_settings(general_frame)
        
        # Deodexing settings tab
        deodex_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(deodex_frame, text="Deodexing")
        self._create_deodex_settings(deodex_frame)
        
        # GUI settings tab
        gui_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(gui_frame, text="Interface")
        self._create_gui_settings(gui_frame)
        
        # Advanced settings tab
        advanced_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(advanced_frame, text="Advanced")
        self._create_advanced_settings(advanced_frame)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_defaults).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Import Settings", command=self._import_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Settings", command=self._export_settings).pack(side=tk.LEFT, padx=5)
    
    def _create_general_settings(self, parent):
        """Create general settings controls"""
        frame = ttk.LabelFrame(parent, text="General Settings", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Debug mode
        self.debug_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Debug Mode", variable=self.debug_var).pack(anchor=tk.W, pady=2)
        
        # Auto-save
        self.autosave_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Auto-save configuration", variable=self.autosave_var).pack(anchor=tk.W, pady=2)
        
        # Check for updates
        self.check_updates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Check for updates on startup", variable=self.check_updates_var).pack(anchor=tk.W, pady=2)
    
    def _create_deodex_settings(self, parent):
        """Create deodexing settings controls"""
        frame = ttk.LabelFrame(parent, text="Default Deodexing Settings", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Default API level
        api_frame = ttk.Frame(frame)
        api_frame.pack(fill=tk.X, pady=5)
        ttk.Label(api_frame, text="Default API Level:").pack(side=tk.LEFT)
        self.default_api_var = tk.StringVar(value="29")
        ttk.Spinbox(api_frame, from_=1, to=34, width=10, textvariable=self.default_api_var).pack(side=tk.LEFT, padx=(10, 0))
        
        # Max workers
        workers_frame = ttk.Frame(frame)
        workers_frame.pack(fill=tk.X, pady=5)
        ttk.Label(workers_frame, text="Default Max Workers:").pack(side=tk.LEFT)
        self.default_workers_var = tk.StringVar(value="4")
        ttk.Spinbox(workers_frame, from_=1, to=16, width=10, textvariable=self.default_workers_var).pack(side=tk.LEFT, padx=(10, 0))
        
        # Timeout
        timeout_frame = ttk.Frame(frame)
        timeout_frame.pack(fill=tk.X, pady=5)
        ttk.Label(timeout_frame, text="Operation Timeout (seconds):").pack(side=tk.LEFT)
        self.timeout_var = tk.StringVar(value="300")
        ttk.Spinbox(timeout_frame, from_=60, to=1800, width=10, textvariable=self.timeout_var).pack(side=tk.LEFT, padx=(10, 0))
        
        # Auto-detect baksmali
        self.auto_baksmali_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Auto-detect baksmali JAR on startup", variable=self.auto_baksmali_var).pack(anchor=tk.W, pady=2)
    
    def _create_gui_settings(self, parent):
        """Create GUI settings controls"""
        frame = ttk.LabelFrame(parent, text="Interface Settings", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Theme selection
        theme_frame = ttk.Frame(frame)
        theme_frame.pack(fill=tk.X, pady=5)
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value="light")
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, values=["light", "dark"], state="readonly", width=15)
        theme_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Window size
        size_frame = ttk.Frame(frame)
        size_frame.pack(fill=tk.X, pady=5)
        ttk.Label(size_frame, text="Default Window Size:").pack(side=tk.LEFT)
        self.window_width_var = tk.StringVar(value="1200")
        self.window_height_var = tk.StringVar(value="800")
        ttk.Spinbox(size_frame, from_=800, to=2000, width=8, textvariable=self.window_width_var).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Label(size_frame, text="x").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(size_frame, from_=600, to=1500, width=8, textvariable=self.window_height_var).pack(side=tk.LEFT)
        
        # Other GUI options
        self.center_window_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Center window on startup", variable=self.center_window_var).pack(anchor=tk.W, pady=2)
        
        self.remember_tabs_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Remember last active tab", variable=self.remember_tabs_var).pack(anchor=tk.W, pady=2)
    
    def _create_advanced_settings(self, parent):
        """Create advanced settings controls"""
        frame = ttk.LabelFrame(parent, text="Advanced Settings", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Logging level
        log_frame = ttk.Frame(frame)
        log_frame.pack(fill=tk.X, pady=5)
        ttk.Label(log_frame, text="Logging Level:").pack(side=tk.LEFT)
        self.log_level_var = tk.StringVar(value="INFO")
        log_combo = ttk.Combobox(log_frame, textvariable=self.log_level_var, 
                                values=["DEBUG", "INFO", "WARNING", "ERROR"], state="readonly", width=15)
        log_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Database settings
        self.cleanup_db_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Auto-cleanup old job records", variable=self.cleanup_db_var).pack(anchor=tk.W, pady=2)
        
        # Performance settings
        self.monitor_performance_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Monitor system performance", variable=self.monitor_performance_var).pack(anchor=tk.W, pady=2)
        
        # Experimental features
        self.experimental_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Enable experimental features", variable=self.experimental_var).pack(anchor=tk.W, pady=2)
    
    def save_settings(self):
        """Save current settings"""
        try:
            # Update configuration with current values
            settings = {
                'app': {
                    'debug': self.debug_var.get(),
                    'autosave': self.autosave_var.get(),
                    'check_updates': self.check_updates_var.get()
                },
                'deodexing': {
                    'default_api_level': int(self.default_api_var.get()),
                    'max_workers': int(self.default_workers_var.get()),
                    'timeout': int(self.timeout_var.get()),
                    'auto_detect_baksmali': self.auto_baksmali_var.get()
                },
                'gui': {
                    'theme': self.theme_var.get(),
                    'window': {
                        'width': int(self.window_width_var.get()),
                        'height': int(self.window_height_var.get()),
                        'center_on_start': self.center_window_var.get()
                    },
                    'remember_tabs': self.remember_tabs_var.get()
                },
                'advanced': {
                    'log_level': self.log_level_var.get(),
                    'cleanup_database': self.cleanup_db_var.get(),
                    'monitor_performance': self.monitor_performance_var.get(),
                    'experimental_features': self.experimental_var.get()
                }
            }
            
            # Update config object
            self.config.update(settings)
            
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def refresh_settings(self):
        """Refresh settings from config"""
        try:
            # Load values from config
            self.debug_var.set(self.config.get('app.debug', False))
            self.autosave_var.set(self.config.get('app.autosave', True))
            self.check_updates_var.set(self.config.get('app.check_updates', True))
            
            self.default_api_var.set(str(self.config.get('deodexing.default_api_level', 29)))
            self.default_workers_var.set(str(self.config.get('deodexing.max_workers', 4)))
            self.timeout_var.set(str(self.config.get('deodexing.timeout', 300)))
            self.auto_baksmali_var.set(self.config.get('deodexing.auto_detect_baksmali', True))
            
            self.theme_var.set(self.config.get('gui.theme', 'light'))
            self.window_width_var.set(str(self.config.get('gui.window.width', 1200)))
            self.window_height_var.set(str(self.config.get('gui.window.height', 800)))
            self.center_window_var.set(self.config.get('gui.window.center_on_start', True))
            self.remember_tabs_var.set(self.config.get('gui.remember_tabs', True))
            
            self.log_level_var.set(self.config.get('advanced.log_level', 'INFO'))
            self.cleanup_db_var.set(self.config.get('advanced.cleanup_database', True))
            self.monitor_performance_var.set(self.config.get('advanced.monitor_performance', True))
            self.experimental_var.set(self.config.get('advanced.experimental_features', False))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {str(e)}")
    
    def _reset_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            # Set default values
            self.debug_var.set(False)
            self.autosave_var.set(True)
            self.check_updates_var.set(True)
            self.default_api_var.set("29")
            self.default_workers_var.set("4")
            self.timeout_var.set("300")
            self.auto_baksmali_var.set(True)
            self.theme_var.set("light")
            self.window_width_var.set("1200")
            self.window_height_var.set("800")
            self.center_window_var.set(True)
            self.remember_tabs_var.set(True)
            self.log_level_var.set("INFO")
            self.cleanup_db_var.set(True)
            self.monitor_performance_var.set(True)
            self.experimental_var.set(False)
    
    def _import_settings(self):
        """Import settings from file"""
        file_path = filedialog.askopenfilename(
            title="Import Settings",
            filetypes=[("JSON files", "*.json"), ("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if file_path:
            try:
                import json
                with open(file_path, 'r') as f:
                    settings = json.load(f)
                self.config.update(settings)
                self.refresh_settings()
                messagebox.showinfo("Success", "Settings imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import settings: {str(e)}")
    
    def _export_settings(self):
        """Export settings to file"""
        file_path = filedialog.asksaveasfilename(
            title="Export Settings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                import json
                with open(file_path, 'w') as f:
                    json.dump(self.config.to_dict(), f, indent=2)
                messagebox.showinfo("Success", "Settings exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export settings: {str(e)}")


# Add missing imports at the top of the file
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