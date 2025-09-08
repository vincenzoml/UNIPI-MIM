"""
Theme and template management system for markdown slides generator.

This module provides professional academic themes and comprehensive template
management for generating beautiful slides and notes.
"""

from .theme_manager import ThemeManager, AcademicTheme
from .template_manager import TemplateManager, TemplateConfig

__all__ = [
    'ThemeManager',
    'AcademicTheme', 
    'TemplateManager',
    'TemplateConfig'
]