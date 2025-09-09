"""
Configuration Validation System

Validates configuration files and provides detailed error reporting.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import re

from ..utils.logger import get_logger
from ..utils.exceptions import ConfigurationError

logger = get_logger(__name__)


class ConfigValidator:
    """Validates configuration files and provides detailed error reporting."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self, config_data: Dict[str, Any], config_path: Optional[Path] = None) -> None:
        """
        Validate configuration data.
        
        Args:
            config_data: Configuration dictionary to validate
            config_path: Path to configuration file (for error reporting)
            
        Raises:
            ConfigurationError: If validation fails
        """
        self.errors.clear()
        self.warnings.clear()
        
        logger.debug("Starting configuration validation")
        
        try:
            # Validate top-level structure
            self._validate_structure(config_data)
            
            # Validate individual sections
            if 'output' in config_data:
                self._validate_output_config(config_data['output'])
            
            if 'slides' in config_data:
                self._validate_slides_config(config_data['slides'])
            
            if 'notes' in config_data:
                self._validate_notes_config(config_data['notes'])
            
            if 'processing' in config_data:
                self._validate_processing_config(config_data['processing'])
            
            if 'batch' in config_data:
                self._validate_batch_config(config_data['batch'])
            
            if 'logging' in config_data:
                self._validate_logging_config(config_data['logging'])
            
            if 'variables' in config_data:
                self._validate_variables(config_data['variables'])
            
            # Report results
            if self.warnings:
                for warning in self.warnings:
                    logger.warning(f"Configuration warning: {warning}")
            
            if self.errors:
                error_msg = f"Configuration validation failed with {len(self.errors)} error(s)"
                if config_path:
                    error_msg += f" in {config_path}"
                error_msg += ":\n" + "\n".join(f"  • {error}" for error in self.errors)
                raise ConfigurationError(error_msg)
            
            logger.debug("Configuration validation completed successfully")
            
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(f"Validation error: {e}")
    
    def _validate_structure(self, config_data: Dict[str, Any]) -> None:
        """Validate top-level configuration structure."""
        valid_sections = {
            'version', 'name', 'description', 'output', 'slides', 'notes',
            'processing', 'batch', 'logging', 'variables', 'custom'
        }
        
        # Check for unknown sections
        for section in config_data.keys():
            if section not in valid_sections:
                self.warnings.append(f"Unknown configuration section: '{section}'")
        
        # Validate version if present
        if 'version' in config_data:
            version = config_data['version']
            if not isinstance(version, str):
                self.errors.append("'version' must be a string")
            elif not re.match(r'^\d+\.\d+(\.\d+)?$', version):
                self.errors.append("'version' must be in format 'X.Y' or 'X.Y.Z'")
    
    def _validate_output_config(self, output_config: Dict[str, Any]) -> None:
        """Validate output configuration."""
        # Validate formats
        if 'formats' in output_config:
            formats = output_config['formats']
            if not isinstance(formats, list):
                self.errors.append("output.formats must be a list")
            else:
                # Accept Quarto's reveal.js slides identifier as default slides format
                valid_formats = {'html', 'revealjs', 'pdf', 'pptx', 'beamer'}
                for fmt in formats:
                    if fmt not in valid_formats:
                        self.errors.append(f"Invalid output format: '{fmt}'. Valid formats: {', '.join(valid_formats)}")
        
        # Validate directory
        if 'directory' in output_config:
            directory = output_config['directory']
            if not isinstance(directory, str):
                self.errors.append("output.directory must be a string")
            else:
                # Check if directory path is valid (but don't require it to exist)
                try:
                    path = Path(directory)
                    if path.is_absolute() and not path.parent.exists():
                        self.errors.append(f"Output directory parent does not exist: {directory}")
                except (OSError, ValueError):
                    self.errors.append(f"Invalid output directory path: {directory}")
        
        # Validate boolean options
        bool_options = ['preserve_structure', 'overwrite']
        for option in bool_options:
            if option in output_config and not isinstance(output_config[option], bool):
                self.errors.append(f"output.{option} must be a boolean")
        
        # Validate naming pattern
        if 'naming_pattern' in output_config:
            pattern = output_config['naming_pattern']
            if not isinstance(pattern, str):
                self.errors.append("output.naming_pattern must be a string")
            elif '{stem}' not in pattern or '{type}' not in pattern:
                self.warnings.append("output.naming_pattern should contain {stem} and {type} placeholders")
    
    def _validate_slides_config(self, slides_config: Dict[str, Any]) -> None:
        """Validate slides configuration."""
        # Validate theme
        if 'theme' in slides_config:
            theme = slides_config['theme']
            if not isinstance(theme, str):
                self.errors.append("slides.theme must be a string")
            else:
                # Basic theme validation - check against common themes
                common_themes = {
                    'academic-minimal', 'academic-modern', 'academic-classic', 'academic-technical', 'academic-elegant',
                    'dark', 'white', 'black', 'league', 'beige', 'sky',
                    'night', 'serif', 'simple', 'solarized', 'blood', 'moon'
                }
                if theme not in common_themes and not theme.startswith('custom-'):
                    self.errors.append(f"Unknown theme '{theme}'. Available themes: {', '.join(sorted(common_themes))}")
        
        # Validate numeric options
        numeric_options = {
            'max_content_length': (100, 10000),
            'auto_slide': (0, 60000),
            'viewport_width': (320, 4096),
            'viewport_height': (240, 2160),
        }
        
        for option, (min_val, max_val) in numeric_options.items():
            if option in slides_config:
                value = slides_config[option]
                if not isinstance(value, int):
                    self.errors.append(f"slides.{option} must be an integer")
                elif not (min_val <= value <= max_val):
                    self.errors.append(f"slides.{option} must be between {min_val} and {max_val}")
        
        # Validate float options
        if 'viewport_scale' in slides_config:
            scale = slides_config['viewport_scale']
            if not isinstance(scale, (int, float)):
                self.errors.append("slides.viewport_scale must be a number")
            elif not (0.1 <= scale <= 5.0):
                self.errors.append("slides.viewport_scale must be between 0.1 and 5.0")
        
        # Validate boolean options
        bool_options = [
            'auto_split', 'controls', 'progress', 'center', 'touch', 'loop',
            'rtl', 'shuffle', 'fragments', 'embedded', 'help', 'show_notes',
            'auto_slide_stoppable', 'mouse_wheel', 'hide_address_bar', 'preview_links'
        ]
        
        for option in bool_options:
            if option in slides_config and not isinstance(slides_config[option], bool):
                self.errors.append(f"slides.{option} must be a boolean")
        
        # Validate string options with choices
        string_choices = {
            'transition': ['none', 'fade', 'slide', 'convex', 'concave', 'zoom'],
            'navigation_mode': ['default', 'linear', 'grid']
        }
        
        for option, choices in string_choices.items():
            if option in slides_config:
                value = slides_config[option]
                if not isinstance(value, str):
                    self.errors.append(f"slides.{option} must be a string")
                elif value not in choices:
                    self.errors.append(f"slides.{option} must be one of: {', '.join(choices)}")
    
    def _validate_notes_config(self, notes_config: Dict[str, Any]) -> None:
        """Validate notes configuration."""
        # Validate style
        if 'style' in notes_config:
            style = notes_config['style']
            if not isinstance(style, str):
                self.errors.append("notes.style must be a string")
        
        # Validate boolean options
        bool_options = [
            'include_toc', 'page_numbers', 'line_numbers', 'margin_notes',
            'bibliography', 'cross_references', 'figure_captions',
            'table_captions', 'equation_numbers'
        ]
        
        for option in bool_options:
            if option in notes_config and not isinstance(notes_config[option], bool):
                self.errors.append(f"notes.{option} must be a boolean")
        
        # Validate list options
        if 'header_includes' in notes_config:
            header_includes = notes_config['header_includes']
            if not isinstance(header_includes, list):
                self.errors.append("notes.header_includes must be a list")
            elif not all(isinstance(item, str) for item in header_includes):
                self.errors.append("notes.header_includes must be a list of strings")
        
        # Validate string options
        string_options = ['geometry', 'font_size', 'font_family', 'line_spacing']
        for option in string_options:
            if option in notes_config and not isinstance(notes_config[option], str):
                self.errors.append(f"notes.{option} must be a string")
        
        # Validate template path
        if 'template' in notes_config:
            template = notes_config['template']
            if template is not None:
                if not isinstance(template, str):
                    self.errors.append("notes.template must be a string")
                else:
                    template_path = Path(template)
                    if template_path.is_absolute() and not template_path.exists():
                        self.errors.append(f"Notes template file does not exist: {template}")
    
    def _validate_processing_config(self, processing_config: Dict[str, Any]) -> None:
        """Validate processing configuration."""
        # Validate boolean options
        bool_options = [
            'intelligent_splitting', 'preserve_formatting', 'syntax_highlighting',
            'image_optimization', 'link_validation', 'content_validation'
        ]
        
        for option in bool_options:
            if option in processing_config and not isinstance(processing_config[option], bool):
                self.errors.append(f"processing.{option} must be a boolean")
        
        # Validate math renderer
        if 'math_renderer' in processing_config:
            renderer = processing_config['math_renderer']
            valid_renderers = ['mathjax', 'katex', 'native']
            if not isinstance(renderer, str):
                self.errors.append("processing.math_renderer must be a string")
            elif renderer not in valid_renderers:
                self.errors.append(f"processing.math_renderer must be one of: {', '.join(valid_renderers)}")
        
        # Validate LaTeX packages
        if 'latex_packages' in processing_config:
            packages = processing_config['latex_packages']
            if not isinstance(packages, list):
                self.errors.append("processing.latex_packages must be a list")
            elif not all(isinstance(pkg, str) for pkg in packages):
                self.errors.append("processing.latex_packages must be a list of strings")
        
        # Validate custom commands
        if 'custom_commands' in processing_config:
            commands = processing_config['custom_commands']
            if not isinstance(commands, dict):
                self.errors.append("processing.custom_commands must be a dictionary")
            elif not all(isinstance(k, str) and isinstance(v, str) for k, v in commands.items()):
                self.errors.append("processing.custom_commands must be a dictionary of string key-value pairs")
    
    def _validate_batch_config(self, batch_config: Dict[str, Any]) -> None:
        """Validate batch processing configuration."""
        # Validate string options
        string_options = ['pattern', 'error_handling']
        for option in string_options:
            if option in batch_config and not isinstance(batch_config[option], str):
                self.errors.append(f"batch.{option} must be a string")
        
        # Validate error handling
        if 'error_handling' in batch_config:
            error_handling = batch_config['error_handling']
            valid_options = ['continue', 'stop', 'skip']
            if error_handling not in valid_options:
                self.errors.append(f"batch.error_handling must be one of: {', '.join(valid_options)}")
        
        # Validate boolean options
        bool_options = ['recursive', 'parallel', 'progress_reporting']
        for option in bool_options:
            if option in batch_config and not isinstance(batch_config[option], bool):
                self.errors.append(f"batch.{option} must be a boolean")
        
        # Validate max_workers
        if 'max_workers' in batch_config:
            max_workers = batch_config['max_workers']
            if not isinstance(max_workers, int):
                self.errors.append("batch.max_workers must be an integer")
            elif not (1 <= max_workers <= 32):
                self.errors.append("batch.max_workers must be between 1 and 32")
        
        # Validate list options
        list_options = ['file_filters', 'exclude_patterns']
        for option in list_options:
            if option in batch_config:
                value = batch_config[option]
                if not isinstance(value, list):
                    self.errors.append(f"batch.{option} must be a list")
                elif not all(isinstance(item, str) for item in value):
                    self.errors.append(f"batch.{option} must be a list of strings")
    
    def _validate_logging_config(self, logging_config: Dict[str, Any]) -> None:
        """Validate logging configuration."""
        # Validate log level
        if 'level' in logging_config:
            level = logging_config['level']
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if not isinstance(level, str):
                self.errors.append("logging.level must be a string")
            elif level.upper() not in valid_levels:
                self.errors.append(f"logging.level must be one of: {', '.join(valid_levels)}")
        
        # Validate string options
        string_options = ['format', 'file', 'max_size']
        for option in string_options:
            if option in logging_config and logging_config[option] is not None:
                if not isinstance(logging_config[option], str):
                    self.errors.append(f"logging.{option} must be a string")
        
        # Validate backup_count
        if 'backup_count' in logging_config:
            backup_count = logging_config['backup_count']
            if not isinstance(backup_count, int):
                self.errors.append("logging.backup_count must be an integer")
            elif not (0 <= backup_count <= 100):
                self.errors.append("logging.backup_count must be between 0 and 100")
        
        # Validate boolean options
        bool_options = ['console', 'colors']
        for option in bool_options:
            if option in logging_config and not isinstance(logging_config[option], bool):
                self.errors.append(f"logging.{option} must be a boolean")
    
    def _validate_variables(self, variables: Dict[str, Any]) -> None:
        """Validate user-defined variables."""
        if not isinstance(variables, dict):
            self.errors.append("variables must be a dictionary")
            return
        
        # Check for reserved variable names
        reserved_names = {'config', 'output', 'slides', 'notes', 'processing', 'batch', 'logging'}
        for var_name in variables.keys():
            if var_name in reserved_names:
                self.warnings.append(f"Variable name '{var_name}' conflicts with reserved configuration section")
        
        # Validate variable values (should be serializable)
        for var_name, var_value in variables.items():
            if not isinstance(var_name, str):
                self.errors.append(f"Variable name must be a string, got {type(var_name).__name__}")
            
            # Check if value is serializable (basic types)
            if not self._is_serializable(var_value):
                self.warnings.append(f"Variable '{var_name}' has complex type that may not serialize properly")
    
    def _is_serializable(self, value: Any) -> bool:
        """Check if a value is serializable to YAML."""
        if value is None:
            return True
        if isinstance(value, (bool, int, float, str)):
            return True
        if isinstance(value, (list, tuple)):
            return all(self._is_serializable(item) for item in value)
        if isinstance(value, dict):
            return all(
                isinstance(k, str) and self._is_serializable(v)
                for k, v in value.items()
            )
        return False