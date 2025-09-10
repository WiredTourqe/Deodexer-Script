#!/usr/bin/env python3
"""
Launch GUI for manual testing and verification
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    try:
        print("🚀 Launching Deodexer Pro GUI...")
        print("✨ Features available:")
        print("   • Complete job manager with folder selection")
        print("   • Auto-detection of Java and baksmali")
        print("   • Self-contained baksmali download")
        print("   • Real-time progress monitoring")
        print("   • File browser for ODEX exploration")
        print("   • Advanced configuration settings")
        print()
        print("💡 Quick Start:")
        print("   1. Go to 'Job Manager' tab")
        print("   2. Select input folder with ODEX files")
        print("   3. Choose output directory")
        print("   4. Click 'Auto-detect' for baksmali JAR")
        print("   5. Click 'Validate Setup' to check configuration")
        print("   6. Click 'Start Deodexing' to begin")
        print()
        
        # Launch GUI
        from deodexer_pro.main import main
        sys.argv = ['main.py', 'gui']
        main()
        
    except ImportError as e:
        print(f"❌ GUI startup failed: {e}")
        print("🔧 Fallback: Testing core functionality...")
        
        # Test core components
        from deodexer_pro.core.deodexer import DeodexerEngine
        from deodexer_pro.core.config import config
        
        engine = DeodexerEngine()
        print(f"✅ Deodexer engine initialized")
        print(f"✅ Configuration loaded: {config.get('app.name', 'Unknown')}")
        print(f"✅ Java environment: {'Working' if engine._check_prerequisites() else 'Issues'}")
        
        print("\n📋 To manually launch GUI:")
        print("   python -m src.deodexer_pro.main gui")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()