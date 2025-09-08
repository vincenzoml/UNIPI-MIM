"""Configuration management for Markdown Slides Generator."""

from .config_manager import ConfigManager, Config
from .validation import ConfigValidator

__all__ = ['ConfigManager', 'Config', 'ConfigValidator']