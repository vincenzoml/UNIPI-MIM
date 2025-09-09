"""
Configuration Management System

Handles YAML configuration files with validation and error reporting.
"""

import yaml
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Union
import os

from ..utils.logger import get_logger
from ..utils.exceptions import ConfigurationError
from .validation import ConfigValidator

logger = get_logger(__name__)


@dataclass
class OutputConfig:
    """Configuration for output generation."""
    formats: List[str] = field(default_factory=lambda: ['revealjs'])
    directory: str = './output'
    preserve_structure: bool = True
    overwrite: bool = False
    naming_pattern: str = '{stem}_{type}.{ext}'


@dataclass
class SlideConfig:
    """Configuration for slide generation."""
    theme: str = 'academic-minimal'
    template: Optional[str] = None
    max_content_length: int = 1000
    auto_split: bool = True
    transition: str = 'slide'
    controls: bool = True
    progress: bool = True
    center: bool = True
    touch: bool = True
    loop: bool = False
    rtl: bool = False
    navigation_mode: str = 'default'
    shuffle: bool = False
    fragments: bool = True
    embedded: bool = False
    help: bool = True
    show_notes: bool = False
    auto_slide: int = 0
    auto_slide_stoppable: bool = True
    mouse_wheel: bool = False
    hide_address_bar: bool = True
    preview_links: bool = False
    viewport_width: int = 1024
    viewport_height: int = 768
    viewport_scale: float = 1.0


@dataclass
class NotesConfig:
    """Configuration for notes generation."""
    style: str = 'academic'
    template: Optional[str] = None
    include_toc: bool = True
    page_numbers: bool = True
    line_numbers: bool = False
    margin_notes: bool = False
    bibliography: bool = True
    cross_references: bool = True
    figure_captions: bool = True
    table_captions: bool = True
    equation_numbers: bool = True
    header_includes: List[str] = field(default_factory=list)
    geometry: str = 'margin=1in'
    font_size: str = '11pt'
    font_family: str = 'default'
    line_spacing: str = 'single'


@dataclass
class ProcessingConfig:
    """Configuration for content processing."""
    intelligent_splitting: bool = True
    preserve_formatting: bool = True
    syntax_highlighting: bool = True
    math_renderer: str = 'mathjax'
    latex_packages: List[str] = field(default_factory=list)
    custom_commands: Dict[str, str] = field(default_factory=dict)
    image_optimization: bool = True
    link_validation: bool = False
    content_validation: bool = True


@dataclass
class BatchConfig:
    """Configuration for batch processing."""
    pattern: str = '*.md'
    recursive: bool = False
    parallel: bool = True
    max_workers: int = 4
    progress_reporting: bool = True
    error_handling: str = 'continue'  # 'continue', 'stop', 'skip'
    file_filters: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = 'INFO'
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file: Optional[str] = None
    max_size: str = '10MB'
    backup_count: int = 5
    console: bool = True
    colors: bool = True


@dataclass
class Config:
    """Main configuration class."""
    # Metadata
    version: str = '1.0'
    name: str = 'default'
    description: str = 'Default configuration'
    
    # Core configurations
    output: OutputConfig = field(default_factory=OutputConfig)
    slides: SlideConfig = field(default_factory=SlideConfig)
    notes: NotesConfig = field(default_factory=NotesConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    batch: BatchConfig = field(default_factory=BatchConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # User-defined variables
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Custom settings
    custom: Dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """Manages configuration loading, validation, and merging."""
    
    def __init__(self):
        self.validator = ConfigValidator()
        self._config_cache: Dict[str, Config] = {}
        
    def load_config(self, config_path: Optional[Union[str, Path]] = None) -> Config:
        """
        Load configuration from file or return default configuration.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Config: Loaded and validated configuration
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        if config_path is None:
            logger.debug("No config file specified, using default configuration")
            return Config()
        
        config_path = Path(config_path)
        
        # Check cache
        cache_key = str(config_path.absolute())
        if cache_key in self._config_cache:
            logger.debug(f"Using cached configuration from {config_path}")
            return self._config_cache[cache_key]
        
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        try:
            logger.info(f"Loading configuration from {config_path}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}
            
            # Validate configuration
            self.validator.validate(config_data, config_path)
            
            # Create config object
            config = self._create_config_from_dict(config_data)
            
            # Cache the configuration
            self._config_cache[cache_key] = config
            
            logger.debug(f"Successfully loaded configuration: {config.name}")
            return config
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {config_path}: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration from {config_path}: {e}")
    
    def merge_configs(self, base_config: Config, override_config: Config) -> Config:
        """
        Merge two configurations, with override_config taking precedence.
        
        Args:
            base_config: Base configuration
            override_config: Configuration to merge on top
            
        Returns:
            Config: Merged configuration
        """
        logger.debug("Merging configurations")
        
        # Convert to dictionaries for easier merging
        base_dict = asdict(base_config)
        override_dict = asdict(override_config)
        
        # Deep merge dictionaries
        merged_dict = self._deep_merge(base_dict, override_dict)
        
        # Create new config from merged dictionary
        return self._create_config_from_dict(merged_dict)
    
    def merge_cli_options(self, config: Config, cli_options: Dict[str, Any]) -> Config:
        """
        Merge CLI options into configuration.
        
        Args:
            config: Base configuration
            cli_options: CLI options to merge
            
        Returns:
            Config: Configuration with CLI options applied
        """
        logger.debug("Merging CLI options into configuration")
        
        # Create a copy of the config
        config_dict = asdict(config)
        
        # Map CLI options to configuration paths
        # Map simple CLI options to config paths. Boolean flags like 'verbose' and
        # 'quiet' are handled specially below to avoid accidentally writing raw
        # booleans into string fields (which caused .upper() on a bool).
        cli_mapping = {
            'format': ('output', 'formats'),
            'output_dir': ('output', 'directory'),
            'theme': ('slides', 'theme'),
            'template': ('slides', 'template'),
            'author': ('variables', 'author'),
            'title': ('variables', 'title'),
            'date': ('variables', 'date'),
            'institute': ('variables', 'institute'),
        }
        
        # Apply CLI options
        for cli_key, config_path in cli_mapping.items():
            if cli_key in cli_options and cli_options[cli_key] is not None:
                value = cli_options[cli_key]

                # Special handling for some options
                if cli_key == 'format':
                    # click passes multiple --format options as a tuple; convert to list
                    if isinstance(value, (list, tuple)):
                        value = list(value)

                # Set the value in config dictionary
                self._set_nested_value(config_dict, config_path, value)

        # Handle boolean flags that map to logging level explicitly. Only
        # apply them when True to avoid setting the logging.level to a boolean
        # (which later code calls .upper() on).
        if 'verbose' in cli_options and cli_options.get('verbose'):
            self._set_nested_value(config_dict, ('logging', 'level'), 'DEBUG')
        elif 'quiet' in cli_options and cli_options.get('quiet'):
            self._set_nested_value(config_dict, ('logging', 'level'), 'WARNING')
        
        return self._create_config_from_dict(config_dict)
    
    def save_config(self, config: Config, config_path: Union[str, Path]) -> None:
        """
        Save configuration to YAML file.
        
        Args:
            config: Configuration to save
            config_path: Path to save configuration file
        """
        config_path = Path(config_path)
        
        try:
            logger.info(f"Saving configuration to {config_path}")
            
            # Ensure directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dictionary and save
            config_dict = asdict(config)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2, sort_keys=False)
            
            logger.debug(f"Configuration saved successfully")
            
        except Exception as e:
            raise ConfigurationError(f"Error saving configuration to {config_path}: {e}")
    
    def create_default_config(self, config_path: Union[str, Path]) -> Config:
        """
        Create and save a default configuration file.
        
        Args:
            config_path: Path to create configuration file
            
        Returns:
            Config: Default configuration
        """
        config = Config()
        config.name = 'user-default'
        config.description = 'User default configuration'
        
        self.save_config(config, config_path)
        return config
    
    def get_config_template(self) -> str:
        """
        Get a YAML template for configuration file.
        
        Returns:
            str: YAML configuration template
        """
        template_config = Config()
        template_config.name = 'my-config'
        template_config.description = 'Custom configuration for my lectures'
        
        # Add some example customizations
        template_config.slides.theme = 'academic-modern'
        template_config.slides.transition = 'fade'
        template_config.notes.style = 'technical'
        template_config.variables = {
            'author': 'Your Name',
            'institute': 'Your Institution',
            'course': 'Course Name'
        }
        
        config_dict = asdict(template_config)
        return yaml.dump(config_dict, default_flow_style=False, indent=2, sort_keys=False)
    
    def _create_config_from_dict(self, config_data: Dict[str, Any]) -> Config:
        """Create Config object from dictionary."""
        try:
            # Handle nested configurations
            output_data = config_data.get('output', {})
            slides_data = config_data.get('slides', {})
            notes_data = config_data.get('notes', {})
            processing_data = config_data.get('processing', {})
            batch_data = config_data.get('batch', {})
            logging_data = config_data.get('logging', {})
            
            return Config(
                version=config_data.get('version', '1.0'),
                name=config_data.get('name', 'default'),
                description=config_data.get('description', 'Configuration'),
                output=OutputConfig(**output_data),
                slides=SlideConfig(**slides_data),
                notes=NotesConfig(**notes_data),
                processing=ProcessingConfig(**processing_data),
                batch=BatchConfig(**batch_data),
                logging=LoggingConfig(**logging_data),
                variables=config_data.get('variables', {}),
                custom=config_data.get('custom', {})
            )
        except TypeError as e:
            raise ConfigurationError(f"Invalid configuration structure: {e}")
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _set_nested_value(self, config_dict: Dict, path: tuple, value: Any) -> None:
        """Set a nested value in configuration dictionary."""
        current = config_dict
        
        # Navigate to the parent of the target key
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[path[-1]] = value


# Global configuration manager instance
config_manager = ConfigManager()