"""
Comprehensive error handling infrastructure for Markdown Slides Generator.

Defines custom exception hierarchy with detailed error information,
context, and recovery suggestions for professional error handling.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path


class MarkdownSlidesError(Exception):
    """
    Base exception for all Markdown Slides Generator errors.
    
    Provides structured error information with context and suggestions
    for recovery or troubleshooting.
    """
    
    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        error_code: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.suggestions = suggestions or []
        self.error_code = error_code
    
    def __str__(self) -> str:
        """Format error message with context and suggestions."""
        result = [self.message]
        
        if self.error_code:
            result.append(f"Error Code: {self.error_code}")
        
        if self.context:
            result.append("Context:")
            for key, value in self.context.items():
                result.append(f"  {key}: {value}")
        
        if self.suggestions:
            result.append("Suggestions:")
            for suggestion in self.suggestions:
                result.append(f"  • {suggestion}")
        
        return "\n".join(result)


class InputError(MarkdownSlidesError):
    """Errors related to input files and content validation."""
    
    def __init__(
        self,
        message: str,
        file_path: Optional[Path] = None,
        line_number: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if file_path:
            context['file_path'] = str(file_path)
        if line_number:
            context['line_number'] = line_number
        
        super().__init__(message, context=context, **kwargs)
        self.file_path = file_path
        self.line_number = line_number


class FileNotFoundError(InputError):
    """Specific error for missing input files."""
    
    def __init__(self, file_path: Path):
        super().__init__(
            f"Input file not found: {file_path}",
            file_path=file_path,
            suggestions=[
                "Check that the file path is correct",
                "Verify the file exists and is readable",
                "Use absolute path if relative path is not working"
            ],
            error_code="INPUT_001"
        )


class InvalidMarkdownError(InputError):
    """Error for malformed or invalid markdown content."""
    
    def __init__(
        self,
        message: str,
        file_path: Optional[Path] = None,
        line_number: Optional[int] = None,
        markdown_content: Optional[str] = None
    ):
        context = {}
        if markdown_content:
            context['content_preview'] = markdown_content[:100] + "..." if len(markdown_content) > 100 else markdown_content
        
        super().__init__(
            message,
            file_path=file_path,
            line_number=line_number,
            context=context,
            suggestions=[
                "Check markdown syntax for errors",
                "Validate special comment directives",
                "Ensure proper header structure"
            ],
            error_code="INPUT_002"
        )


class ProcessingError(MarkdownSlidesError):
    """Errors during content processing and transformation."""
    
    def __init__(
        self,
        message: str,
        processing_stage: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if processing_stage:
            context['processing_stage'] = processing_stage
        
        super().__init__(message, context=context, **kwargs)
        self.processing_stage = processing_stage


class ContentSplittingError(ProcessingError):
    """Error during content splitting between slides and notes."""
    
    def __init__(
        self,
        message: str,
        directive: Optional[str] = None,
        line_number: Optional[int] = None
    ):
        context = {}
        if directive:
            context['directive'] = directive
        if line_number:
            context['line_number'] = line_number
        
        super().__init__(
            message,
            processing_stage="content_splitting",
            context=context,
            suggestions=[
                "Check special comment directive syntax",
                "Ensure directives are properly closed",
                "Verify directive nesting is correct"
            ],
            error_code="PROC_001"
        )


class LaTeXError(ProcessingError):
    """Errors related to LaTeX processing and math rendering."""
    
    def __init__(
        self,
        message: str,
        latex_code: Optional[str] = None,
        line_number: Optional[int] = None,
        latex_error: Optional[str] = None
    ):
        context = {}
        if latex_code:
            context['latex_code'] = latex_code
        if line_number:
            context['line_number'] = line_number
        if latex_error:
            context['latex_error'] = latex_error
        
        super().__init__(
            message,
            processing_stage="latex_processing",
            context=context,
            suggestions=[
                "Check LaTeX syntax for mathematical expressions",
                "Verify all LaTeX commands are supported",
                "Ensure proper escaping of special characters",
                "Test LaTeX code in a LaTeX editor first"
            ],
            error_code="PROC_002"
        )


class OutputError(MarkdownSlidesError):
    """Errors during output generation and file writing."""
    
    def __init__(
        self,
        message: str,
        output_format: Optional[str] = None,
        output_path: Optional[Path] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if output_format:
            context['output_format'] = output_format
        if output_path:
            context['output_path'] = str(output_path)
        
        super().__init__(message, context=context, **kwargs)
        self.output_format = output_format
        self.output_path = output_path


class QuartoError(OutputError):
    """Errors from Quarto processing and rendering."""
    
    def __init__(
        self,
        message: str,
        quarto_command: Optional[str] = None,
        quarto_output: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if quarto_command:
            context['quarto_command'] = quarto_command
        if quarto_output:
            context['quarto_output'] = quarto_output[:500] + "..." if len(quarto_output) > 500 else quarto_output
        
        super().__init__(
            message,
            context=context,
            suggestions=[
                "Check that Quarto is properly installed",
                "Verify Quarto version compatibility",
                "Check Quarto configuration and templates",
                "Run 'quarto check' to verify dependencies"
            ],
            error_code="OUT_001",
            **kwargs
        )


class TemplateError(OutputError):
    """Errors related to template processing and customization."""
    
    def __init__(
        self,
        message: str,
        template_name: Optional[str] = None,
        template_path: Optional[Path] = None
    ):
        context = {}
        if template_name:
            context['template_name'] = template_name
        if template_path:
            context['template_path'] = str(template_path)
        
        super().__init__(
            message,
            context=context,
            suggestions=[
                "Check template file exists and is readable",
                "Verify template syntax is correct",
                "Ensure template variables are properly defined"
            ],
            error_code="OUT_002"
        )


class ConfigurationError(MarkdownSlidesError):
    """Errors related to configuration and settings."""
    
    def __init__(
        self,
        message: str,
        config_file: Optional[Path] = None,
        config_key: Optional[str] = None
    ):
        context = {}
        if config_file:
            context['config_file'] = str(config_file)
        if config_key:
            context['config_key'] = config_key
        
        super().__init__(
            message,
            context=context,
            suggestions=[
                "Check configuration file syntax (YAML)",
                "Verify all required configuration keys are present",
                "Validate configuration values are correct type",
                "Use example configuration as reference"
            ],
            error_code="CONFIG_001"
        )


class DependencyError(MarkdownSlidesError):
    """Errors related to missing or incompatible dependencies."""
    
    def __init__(
        self,
        message: str,
        dependency: Optional[str] = None,
        required_version: Optional[str] = None,
        found_version: Optional[str] = None
    ):
        context = {}
        if dependency:
            context['dependency'] = dependency
        if required_version:
            context['required_version'] = required_version
        if found_version:
            context['found_version'] = found_version
        
        super().__init__(
            message,
            context=context,
            suggestions=[
                "Install missing dependencies using package manager",
                "Update dependencies to required versions",
                "Check system PATH for executable dependencies",
                "Run dependency check command for detailed status"
            ],
            error_code="DEP_001"
        )


def handle_exception(func):
    """
    Decorator to provide consistent exception handling and logging.
    
    Converts unexpected exceptions into MarkdownSlidesError with context.
    """
    import functools
    from .logger import get_logger
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        try:
            return func(*args, **kwargs)
        except MarkdownSlidesError:
            # Re-raise our custom exceptions as-is
            raise
        except FileNotFoundError as e:
            logger.error(f"File not found in {func.__name__}: {e}")
            raise FileNotFoundError(Path(str(e)))
        except PermissionError as e:
            logger.error(f"Permission error in {func.__name__}: {e}")
            raise OutputError(
                f"Permission denied: {e}",
                suggestions=[
                    "Check file and directory permissions",
                    "Ensure output directory is writable",
                    "Run with appropriate user privileges"
                ]
            )
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise MarkdownSlidesError(
                f"Unexpected error in {func.__name__}: {e}",
                context={'function': func.__name__, 'args': str(args)[:100]},
                suggestions=[
                    "Check input parameters and file paths",
                    "Enable verbose logging for more details",
                    "Report this error if it persists"
                ]
            )
    
    return wrapper