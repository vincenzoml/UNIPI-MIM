"""
Content Validation and Quality Assurance Module

Provides comprehensive validation for slide content, LaTeX expressions,
links, images, and media files with automatic optimization suggestions.
"""

from .content_validator import (
    ContentValidator,
    ValidationResult,
    ValidationIssue,
    IssueType,
    IssueSeverity
)
from .slide_optimizer import (
    SlideOptimizer,
    OptimizationResult,
    OptimizationSuggestion,
    OptimizedContentSplitter
)
from .link_checker import LinkChecker, LinkValidationResult, check_links_sync
from .image_validator import ImageValidator, ImageValidationResult
from .quality_analyzer import QualityAnalyzer, QualityReport

__all__ = [
    'ContentValidator',
    'ValidationResult',
    'ValidationIssue',
    'IssueType',
    'IssueSeverity',
    'SlideOptimizer',
    'OptimizationResult',
    'OptimizationSuggestion',
    'OptimizedContentSplitter',
    'LinkChecker',
    'LinkValidationResult',
    'check_links_sync',
    'ImageValidator',
    'ImageValidationResult',
    'QualityAnalyzer',
    'QualityReport'
]