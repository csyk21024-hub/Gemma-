"""
Tests for the Configuration module
"""

import pytest
import sys
import os
import tempfile
import yaml

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.config import Config
import src.utils.config as config_module


@pytest.fixture(autouse=True)
def reset_global_config():
    """Reset the global config instance before each test"""
    config_module._config_instance = None
    yield
    config_module._config_instance = None


class TestConfig:
    """Tests for Config class"""
    
    def test_default_config(self):
        """Test default configuration is loaded"""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            config_path = f.name
        
        try:
            config = Config(config_path)
            
            # Check default values
            assert config.get("gemma", "model") == "gemma-3-4b"
            assert config.get("ui", "language") == "ja"
            assert config.get("features", "email_proofreading") is True
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def test_get_nested_value(self):
        """Test getting nested values"""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            config_path = f.name
        
        try:
            config = Config(config_path)
            
            value = config.get("gemma", "temperature")
            assert value == 0.7
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def test_get_with_default(self):
        """Test getting value with default"""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            config_path = f.name
        
        try:
            config = Config(config_path)
            
            value = config.get("nonexistent", "key", default="default_value")
            assert value == "default_value"
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def test_set_value(self):
        """Test setting a value"""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            config_path = f.name
        
        try:
            config = Config(config_path)
            
            config.set("gemma", "model", value="gemma-3-12b")
            assert config.get("gemma", "model") == "gemma-3-12b"
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration"""
        config_path = tempfile.mktemp(suffix='.yaml')
        
        try:
            # Create and modify config
            config1 = Config(config_path)
            config1.set("gemma", "model", value="gemma-3-27b")
            config1.save_config()
            
            # Load in new instance
            config2 = Config(config_path)
            assert config2.get("gemma", "model") == "gemma-3-27b"
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def test_get_gemma_model(self):
        """Test getting Gemma model"""
        config_path = tempfile.mktemp(suffix='.yaml')
        
        try:
            config = Config(config_path)
            model = config.get_gemma_model()
            assert model == "gemma-3-4b"
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def test_set_gemma_model(self):
        """Test setting Gemma model"""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            config_path = f.name
        
        try:
            config = Config(config_path)
            config.set_gemma_model("gemma-3-1b")
            
            assert config.get_gemma_model() == "gemma-3-1b"
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def test_get_available_models(self):
        """Test getting available models"""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            config_path = f.name
        
        try:
            config = Config(config_path)
            models = config.get_available_models()
            
            assert "gemma-3-1b" in models
            assert "gemma-3-4b" in models
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def test_load_existing_config(self):
        """Test loading existing configuration file"""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w') as f:
            yaml.dump({
                "gemma": {
                    "model": "gemma-3-12b",
                    "temperature": 0.5
                }
            }, f)
            config_path = f.name
        
        try:
            config = Config(config_path)
            
            # Custom value should be loaded
            assert config.get("gemma", "model") == "gemma-3-12b"
            assert config.get("gemma", "temperature") == 0.5
            
            # Default values should still be present
            assert config.get("ui", "language") == "ja"
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
