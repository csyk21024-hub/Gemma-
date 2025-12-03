"""
Configuration management for the Gemma Support Tool
"""

import os
import yaml
from typing import Any


class Config:
    """Configuration manager for the application"""
    
    DEFAULT_CONFIG = {
        "gemma": {
            "model": "gemma-3-4b",
            "available_models": [
                "gemma-3-1b",
                "gemma-3-4b",
                "gemma-3-12b",
                "gemma-3-27b"
            ],
            "temperature": 0.7,
            "max_tokens": 2048,
            "api_key": ""
        },
        "ui": {
            "theme": "dark",
            "chat_panel_width": 400,
            "font_size": 12,
            "language": "ja"
        },
        "features": {
            "email_proofreading": True,
            "pdf_summarization": True,
            "word_processing": True,
            "web_search": True,
            "education_mode": True
        },
        "education": {
            "learned_documents_path": "learned_documents",
            "enable_document_learning": True
        },
        "paths": {
            "cache_dir": "cache",
            "logs_dir": "logs"
        }
    }
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize configuration"""
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from file or create default"""
        import copy
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
                return self._merge_config(copy.deepcopy(self.DEFAULT_CONFIG), user_config)
            except (yaml.YAMLError, IOError):
                return copy.deepcopy(self.DEFAULT_CONFIG)
        return copy.deepcopy(self.DEFAULT_CONFIG)
    
    def _merge_config(self, base: dict, override: dict) -> dict:
        """Merge override config into base config"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
    
    def get(self, *keys: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation keys"""
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, *keys: str, value: Any) -> None:
        """Set a configuration value using dot notation keys"""
        if not keys:
            return
        
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
    
    def get_gemma_model(self) -> str:
        """Get the current Gemma model"""
        return self.get("gemma", "model", default="gemma-3-4b")
    
    def set_gemma_model(self, model: str) -> None:
        """Set the Gemma model"""
        self.set("gemma", "model", value=model)
        self.save_config()
    
    def get_available_models(self) -> list:
        """Get available Gemma models"""
        return self.get("gemma", "available_models", default=[])
    
    def get_api_key(self) -> str:
        """Get the Gemma API key"""
        api_key = self.get("gemma", "api_key", default="")
        if not api_key:
            api_key = os.environ.get("GEMMA_API_KEY", "")
        return api_key
    
    def set_api_key(self, api_key: str) -> None:
        """Set the Gemma API key"""
        self.set("gemma", "api_key", value=api_key)
        self.save_config()


# Global config instance
_config_instance = None


def get_config() -> Config:
    """Get the global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
