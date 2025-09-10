"""
Test configuration management
"""

import pytest
import tempfile
import os
from pathlib import Path

# Add src to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from deodexer_pro.core.config import Config


class TestConfig:
    """Test configuration management functionality"""
    
    def test_default_config_creation(self):
        """Test creation of default configuration"""
        config = Config()
        assert config.get('app.name') is not None
        assert config.get('app.version') is not None
    
    def test_config_get_with_default(self):
        """Test getting configuration values with defaults"""
        config = Config()
        
        # Test existing value
        assert config.get('app.name') == 'Deodexer Pro'
        
        # Test non-existing value with default
        assert config.get('non.existing.key', 'default_value') == 'default_value'
        
        # Test non-existing value without default
        assert config.get('non.existing.key') is None
    
    def test_config_set_and_get(self):
        """Test setting and getting configuration values"""
        config = Config()
        
        # Set a value
        config.set('test.setting', 'test_value')
        assert config.get('test.setting') == 'test_value'
        
        # Set nested value
        config.set('test.nested.setting', 42)
        assert config.get('test.nested.setting') == 42
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = Config()
        
        # Valid configuration should pass
        assert config.validate() is True
        
        # Test with invalid max_workers
        original_value = config.get('deodexing.max_workers')
        config.set('deodexing.max_workers', -1)
        assert config.validate() is False
        
        # Restore valid value
        config.set('deodexing.max_workers', original_value)
        assert config.validate() is True
    
    def test_config_to_dict(self):
        """Test configuration to dictionary conversion"""
        config = Config()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert 'app' in config_dict
        assert 'deodexing' in config_dict
    
    def test_config_update(self):
        """Test configuration update functionality"""
        config = Config()
        
        # Update with new configuration
        new_config = {
            'test': {
                'key1': 'value1',
                'key2': 'value2'
            }
        }
        config.update(new_config)
        
        assert config.get('test.key1') == 'value1'
        assert config.get('test.key2') == 'value2'


if __name__ == '__main__':
    pytest.main([__file__])