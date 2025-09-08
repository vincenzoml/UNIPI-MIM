"""
Markdown Slides Generator

A professional tool for converting markdown lecture files into beautiful slides 
and comprehensive academic notes using Quarto.
"""

__version__ = "0.1.0"
__author__ = "Markdown Slides Generator Team"
__email__ = "contact@example.com"

from .cli import main
from .core.content_splitter import ContentSplitter
from .core.quarto_orchestrator import QuartoOrchestrator
from .utils.logger import get_logger
from .utils.exceptions import MarkdownSlidesError

__all__ = [
    "main",
    "ContentSplitter", 
    "QuartoOrchestrator",
    "get_logger",
    "MarkdownSlidesError"
]