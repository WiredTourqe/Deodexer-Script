#!/usr/bin/env python3
"""
Test script to launch GUI and take screenshot
"""

import sys
import os
import threading
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Set up virtual display for headless mode
    os.environ['DISPLAY'] = ':99'
    
    # Start virtual display
    os.system('Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &')
    time.sleep(2)
    
    # Now import and run GUI
    from deodexer_pro.gui.main import DeodexerProGUI
    
    def screenshot_after_delay():
        """Take screenshot after GUI loads"""
        time.sleep(5)  # Wait for GUI to load
        os.system('scrot /tmp/gui_screenshot.png')
        print("Screenshot saved to /tmp/gui_screenshot.png")
    
    # Start screenshot thread
    screenshot_thread = threading.Thread(target=screenshot_after_delay, daemon=True)
    screenshot_thread.start()
    
    # Create and run GUI
    app = DeodexerProGUI()
    
    # Auto-close after 10 seconds
    def auto_close():
        time.sleep(10)
        app.root.quit()
    
    close_thread = threading.Thread(target=auto_close, daemon=True)
    close_thread.start()
    
    print("Starting GUI...")
    app.run()
    
except ImportError as e:
    print(f"Import error: {e}")
    # Try simple test without GUI
    print("Testing basic functionality...")
    
    # Test CLI mode
    print("Testing CLI help...")
    os.system('python -m src.deodexer_pro.main cli --help')
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()