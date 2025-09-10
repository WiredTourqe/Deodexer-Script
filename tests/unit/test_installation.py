"""
Test that the package installation is working correctly
"""

import pytest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))


class TestInstallation:
    """Test package installation and imports"""
    
    def test_package_import(self):
        """Test that the main package can be imported"""
        import deodexer_pro
        assert deodexer_pro is not None
    
    def test_core_modules_import(self):
        """Test that core modules can be imported"""
        from deodexer_pro.core import config, logger
        from deodexer_pro.database import manager, models
        from deodexer_pro.utils import file_utils
        
        assert config is not None
        assert logger is not None
        assert manager is not None
        assert models is not None
        assert file_utils is not None
    
    def test_dependencies_available(self):
        """Test that key dependencies are available"""
        # Test sqlalchemy (database)
        import sqlalchemy
        assert sqlalchemy is not None
        
        # Test requests (networking)
        import requests
        assert requests is not None
        
        # Test flask (web framework)
        import flask
        assert flask is not None
        
        # Test numpy (scientific computing)
        import numpy
        assert numpy is not None
    
    def test_python_magic_import(self):
        """Test that python-magic can be imported (but may not work without libmagic)"""
        try:
            import magic
            # Just test that the module exists, actual functionality requires libmagic
            assert magic is not None
        except ImportError:
            # This is acceptable if libmagic is not installed on the system
            pass
    
    def test_tkinter_tooltip_available(self):
        """Test that tkinter-tooltip package is available (even if can't import due to headless)"""
        # We can't actually import tktooltip in headless environment,
        # but we can check that the package metadata exists
        import pkg_resources
        try:
            pkg_resources.get_distribution('tkinter-tooltip')
        except pkg_resources.DistributionNotFound:
            pytest.fail("tkinter-tooltip package not found")


if __name__ == '__main__':
    pytest.main([__file__])