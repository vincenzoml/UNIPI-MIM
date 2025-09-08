"""
LaTeX Processing Module - Advanced LaTeX validation and processing system.

This module provides comprehensive LaTeX expression validation, syntax checking,
and error reporting with line numbers for malformed LaTeX expressions. It enhances
Quarto's built-in LaTeX support with robust validation and custom command handling.
"""

from .latex_processor import (
    LaTeXProcessor,
    LaTeXExpressionParser,
    LaTeXValidator,
    LaTeXExpression,
    LaTeXExpressionType,
    LaTeXValidationResult
)
from .math_renderer import (
    MathRenderer,
    MathRenderingOptimizer,
    MathCompatibilityChecker,
    MathRenderingConfig,
    MathOptimizationResult,
    MathRenderingEngine,
    OutputFormat
)

__all__ = [
    'LaTeXProcessor',
    'LaTeXExpressionParser', 
    'LaTeXValidator',
    'LaTeXExpression',
    'LaTeXExpressionType',
    'LaTeXValidationResult',
    'MathRenderer',
    'MathRenderingOptimizer',
    'MathCompatibilityChecker',
    'MathRenderingConfig',
    'MathOptimizationResult',
    'MathRenderingEngine',
    'OutputFormat'
]