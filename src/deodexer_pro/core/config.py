"""
Configuration management module for Deodexer Pro
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Advanced configuration management with environment support and validation"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self._config_data: Dict[str, Any] = {}
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path"""
        base_dir = Path(__file__).parent.parent.parent
        return str(base_dir / "config" / "default.yaml")
    
    def _load_config(self) -> None:
        """Load configuration from YAML file with environment variable override"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self._config_data = yaml.safe_load(file) or {}
            
            # Override with environment variables
            self._apply_environment_overrides()
            
        except FileNotFoundError:
            self._config_data = self._get_default_config()
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
    
    def _apply_environment_overrides(self) -> None:
        """Apply environment variable overrides to configuration"""
        env_mappings = {
            'DEODEXER_DB_PATH': ('database', 'path'),
            'DEODEXER_API_PORT': ('api', 'port'),
            'DEODEXER_LOG_LEVEL': ('logging', 'level'),
            'DEODEXER_MAX_WORKERS': ('deodexing', 'max_workers'),
            'DEODEXER_DEBUG': ('app', 'debug'),
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                self._set_nested_value(config_path, env_value)
    
    def _set_nested_value(self, path: tuple, value: str) -> None:
        """Set a nested configuration value"""
        current = self._config_data
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Type conversion
        if value.lower() in ('true', 'false'):
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        
        current[path[-1]] = value
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when no config file is found"""
        return {
            'app': {
                'name': 'Deodexer Pro',
                'version': '2.0.0',
                'debug': False,
                'log_level': 'INFO'
            },
            'database': {
                'type': 'sqlite',
                'path': 'data/deodexer_pro.db'
            },
            'deodexing': {
                'default_api_level': 29,
                'max_workers': 4,
                'timeout': 300,
                'retry_attempts': 3
            },
            'gui': {
                'theme': 'dark',
                'window': {
                    'width': 1200,
                    'height': 800,
                    'resizable': True
                }
            }
        }
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'database.path')"""
        keys = path.split('.')
        current = self._config_data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set(self, path: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = path.split('.')
        current = self._config_data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def save(self, path: Optional[str] = None) -> None:
        """Save configuration to file"""
        save_path = path or self.config_path
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'w', encoding='utf-8') as file:
            yaml.dump(self._config_data, file, default_flow_style=False, indent=2)
    
    def reload(self) -> None:
        """Reload configuration from file"""
        self._load_config()
    
    def validate(self) -> bool:
        """Validate configuration structure and values"""
        required_sections = ['app', 'database', 'deodexing', 'gui']
        
        for section in required_sections:
            if section not in self._config_data:
                return False
        
        # Validate specific values
        if self.get('deodexing.max_workers', 0) <= 0:
            return False
        
        if self.get('deodexing.default_api_level', 0) <= 0:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return self._config_data.copy()
    
    def update(self, new_config: Dict[str, Any]) -> None:
        """Update configuration with new values"""
        self._deep_merge(self._config_data, new_config)
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """Deep merge two dictionaries"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value


# Global configuration instance
config = Config()