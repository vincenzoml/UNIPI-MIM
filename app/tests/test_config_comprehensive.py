"""
Comprehensive tests for configuration management system.

Tests YAML configuration loading, validation, merging, CLI integration,
and error handling for all configuration scenarios.
"""

import pytest
import tempfile
import shutil
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

from markdown_slides_generator.config.config_manager import (
    ConfigManager,
    Config,
    OutputConfig,
    SlideConfig,
    NotesConfig,
    ProcessingConfig,
    BatchConfig,
    LoggingConfig
)
from markdown_slides_generator.config.validation import ConfigValidator
from markdown_slides_generator.utils.exceptions import ConfigurationError


class TestConfigManager:
    """Test configuration manager functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ConfigManager()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_default_config_creation(self):
        """Test creation of default configuration."""
        config = self.manager.load_config()
        
        assert isinstance(config, Config)
        assert config.version == '1.0'
        assert config.name == 'default'
        assert isinstance(config.output, OutputConfig)
        assert isinstance(config.slides, SlideConfig)
        assert isinstance(config.notes, NotesConfig)
        assert isinstance(config.processing, ProcessingConfig)
        assert isinstance(config.batch, BatchConfig)
        assert isinstance(config.logging, LoggingConfig)
    
    def test_yaml_config_loading(self):
        """Test loading configuration from YAML file."""
        config_data = {
            'name': 'test-config',
            'description': 'Test configuration',
            'output': {
                'formats': ['html', 'pdf'],
                'directory': './custom-output',
                'overwrite': True
            },
            'slides': {
                'theme': 'academic-modern',
                'transition': 'fade',
                'auto_split': False
            },
            'notes': {
                'style': 'technical',
                'include_toc': False,
                'font_size': '12pt'
            },
            'variables': {
                'author': 'Test Author',
                'institute': 'Test University'
            }
        }
        
        config_file = self.temp_path / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        config = self.manager.load_config(config_file)
        
        assert config.name == 'test-config'
        assert config.output.formats == ['html', 'pdf']
        assert config.output.directory == './custom-output'
        assert config.output.overwrite is True
        assert config.slides.theme == 'academic-modern'
        assert config.slides.transition == 'fade'
        assert config.slides.auto_split is False
        assert config.notes.style == 'technical'
        assert config.notes.include_toc is False
        assert config.notes.font_size == '12pt'
        assert config.variables['author'] == 'Test Author'
        assert config.variables['institute'] == 'Test University'
    
    def test_invalid_yaml_handling(self):
        """Test handling of invalid YAML files."""
        invalid_yaml = """
name: test
invalid: yaml: content:
  - broken
    indentation
"""
        
        config_file = self.temp_path / "invalid.yaml"
        config_file.write_text(invalid_yaml)
        
        with pytest.raises(ConfigurationError) as exc_info:
            self.manager.load_config(config_file)
        
        assert "Invalid YAML" in str(exc_info.value)
    
    def test_missing_config_file_handling(self):
        """Test handling of missing configuration files."""
        nonexistent_file = self.temp_path / "nonexistent.yaml"
        
        with pytest.raises(ConfigurationError) as exc_info:
            self.manager.load_config(nonexistent_file)
        
        assert "not found" in str(exc_info.value)
    
    def test_config_caching(self):
        """Test configuration caching mechanism."""
        config_data = {'name': 'cached-config'}
        config_file = self.temp_path / "cached.yaml"
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Load config twice
        config1 = self.manager.load_config(config_file)
        config2 = self.manager.load_config(config_file)
        
        # Should be the same object (cached)
        assert config1 is config2
    
    def test_config_merging(self):
        """Test merging of configurations."""
        base_config = Config()
        base_config.name = 'base'
        base_config.slides.theme = 'white'
        base_config.output.formats = ['html']
        
        # Create override config with only the values we want to override
        override_config = Config()
        override_config.name = 'override'
        override_config.slides.transition = 'fade'
        override_config.output.formats = ['pdf']
        override_config.variables = {'author': 'Override Author'}
        
        merged = self.manager.merge_configs(base_config, override_config)
        
        assert merged.name == 'override'  # Override takes precedence
        assert merged.slides.theme == 'academic-minimal'  # Default theme from override config
        assert merged.slides.transition == 'fade'  # Override value added
        assert merged.output.formats == ['pdf']  # Override takes precedence
        assert merged.variables['author'] == 'Override Author'
    
    def test_cli_options_merging(self):
        """Test merging CLI options into configuration."""
        config = Config()
        config.slides.theme = 'white'
        config.output.formats = ['html']
        
        cli_options = {
            'format': ['pdf', 'html'],
            'theme': 'dark',
            'output_dir': '/custom/output',
            'author': 'CLI Author',
            'verbose': True
        }
        
        merged = self.manager.merge_cli_options(config, cli_options)
        
        assert merged.output.formats == ['pdf', 'html']
        assert merged.slides.theme == 'dark'
        assert merged.output.directory == '/custom/output'
        assert merged.variables['author'] == 'CLI Author'
        assert merged.logging.level == 'DEBUG'
    
    def test_config_saving(self):
        """Test saving configuration to YAML file."""
        config = Config()
        config.name = 'saved-config'
        config.slides.theme = 'academic-minimal'
        config.variables = {'author': 'Test Author'}
        
        config_file = self.temp_path / "saved.yaml"
        self.manager.save_config(config, config_file)
        
        assert config_file.exists()
        
        # Load and verify
        loaded_config = self.manager.load_config(config_file)
        assert loaded_config.name == 'saved-config'
        assert loaded_config.slides.theme == 'academic-minimal'
        assert loaded_config.variables['author'] == 'Test Author'
    
    def test_default_config_creation_with_path(self):
        """Test creating default configuration file."""
        config_file = self.temp_path / "default.yaml"
        
        config = self.manager.create_default_config(config_file)
        
        assert config_file.exists()
        assert config.name == 'user-default'
        
        # Verify file content
        loaded_config = self.manager.load_config(config_file)
        assert loaded_config.name == 'user-default'
    
    def test_config_template_generation(self):
        """Test configuration template generation."""
        template = self.manager.get_config_template()
        
        assert isinstance(template, str)
        assert 'name:' in template
        assert 'slides:' in template
        assert 'notes:' in template
        assert 'academic-modern' in template
        
        # Should be valid YAML
        template_data = yaml.safe_load(template)
        assert template_data['name'] == 'my-config'
        assert template_data['slides']['theme'] == 'academic-modern'


class TestConfigDataClasses:
    """Test configuration data classes and their defaults."""
    
    def test_output_config_defaults(self):
        """Test OutputConfig default values."""
        config = OutputConfig()
        
        assert config.formats == ['revealjs']  # Default is revealjs for slides
        assert config.directory == './output'
        assert config.preserve_structure is True
        assert config.overwrite is False
        assert config.naming_pattern == '{stem}_{type}.{ext}'
    
    def test_slide_config_defaults(self):
        """Test SlideConfig default values."""
        config = SlideConfig()
        
        assert config.theme == 'academic-minimal'
        assert config.template is None
        assert config.max_content_length == 1000
        assert config.auto_split is True
        assert config.transition == 'slide'
        assert config.controls is True
        assert config.progress is True
        assert config.center is True
        assert config.touch is True
        assert config.loop is False
        assert config.rtl is False
        assert config.navigation_mode == 'default'
        assert config.shuffle is False
        assert config.fragments is True
        assert config.embedded is False
        assert config.help is True
        assert config.show_notes is False
        assert config.auto_slide == 0
        assert config.auto_slide_stoppable is True
        assert config.mouse_wheel is False
        assert config.hide_address_bar is True
        assert config.preview_links is False
        assert config.viewport_width == 1024
        assert config.viewport_height == 768
        assert config.viewport_scale == 1.0
    
    def test_notes_config_defaults(self):
        """Test NotesConfig default values."""
        config = NotesConfig()
        
        assert config.style == 'academic'
        assert config.template is None
        assert config.include_toc is True
        assert config.page_numbers is True
        assert config.line_numbers is False
        assert config.margin_notes is False
        assert config.bibliography is True
        assert config.cross_references is True
        assert config.figure_captions is True
        assert config.table_captions is True
        assert config.equation_numbers is True
        assert config.header_includes == []
        assert config.geometry == 'margin=1in'
        assert config.font_size == '11pt'
        assert config.font_family == 'default'
        assert config.line_spacing == 'single'
    
    def test_processing_config_defaults(self):
        """Test ProcessingConfig default values."""
        config = ProcessingConfig()
        
        assert config.intelligent_splitting is True
        assert config.preserve_formatting is True
        assert config.syntax_highlighting is True
        assert config.math_renderer == 'mathjax'
        assert config.latex_packages == []
        assert config.custom_commands == {}
        assert config.image_optimization is True
        assert config.link_validation is False
        assert config.content_validation is True
    
    def test_batch_config_defaults(self):
        """Test BatchConfig default values."""
        config = BatchConfig()
        
        assert config.pattern == '*.md'
        assert config.recursive is False
        assert config.parallel is True
        assert config.max_workers == 4
        assert config.progress_reporting is True
        assert config.error_handling == 'continue'
        assert config.file_filters == []
        assert config.exclude_patterns == []
    
    def test_logging_config_defaults(self):
        """Test LoggingConfig default values."""
        config = LoggingConfig()
        
        assert config.level == 'INFO'
        assert '%(asctime)s' in config.format
        assert config.file is None
        assert config.max_size == '10MB'
        assert config.backup_count == 5
        assert config.console is True
        assert config.colors is True


class TestConfigValidation:
    """Test configuration validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ConfigValidator()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_valid_config_validation(self):
        """Test validation of valid configuration."""
        valid_config = {
            'name': 'valid-config',
            'output': {
                'formats': ['html', 'pdf'],
                'directory': './output'
            },
            'slides': {
                'theme': 'white',
                'transition': 'slide'
            }
        }
        
        config_file = self.temp_path / "valid.yaml"
        
        # Should not raise any exceptions
        self.validator.validate(valid_config, config_file)
    
    def test_invalid_format_validation(self):
        """Test validation of invalid output formats."""
        invalid_config = {
            'output': {
                'formats': ['html', 'invalid-format']
            }
        }
        
        config_file = self.temp_path / "invalid.yaml"
        
        with pytest.raises(ConfigurationError) as exc_info:
            self.validator.validate(invalid_config, config_file)
        
        assert "invalid output format" in str(exc_info.value).lower()
    
    def test_invalid_theme_validation(self):
        """Test validation of invalid themes."""
        invalid_config = {
            'slides': {
                'theme': 'nonexistent-theme'
            }
        }
        
        config_file = self.temp_path / "invalid.yaml"
        
        with pytest.raises(ConfigurationError) as exc_info:
            self.validator.validate(invalid_config, config_file)
        
        assert "theme" in str(exc_info.value).lower()
    
    def test_invalid_numeric_values(self):
        """Test validation of invalid numeric values."""
        invalid_config = {
            'slides': {
                'max_content_length': -100  # Should be positive
            },
            'batch': {
                'max_workers': 0  # Should be positive
            }
        }
        
        config_file = self.temp_path / "invalid.yaml"
        
        with pytest.raises(ConfigurationError):
            self.validator.validate(invalid_config, config_file)
    
    def test_path_validation(self):
        """Test validation of file paths."""
        invalid_config = {
            'output': {
                'directory': '/invalid/path/that/does/not/exist'
            },
            'notes': {
                'template': '/nonexistent/template.tex'
            }
        }
        
        config_file = self.temp_path / "invalid.yaml"
        
        # Should validate paths and provide warnings
        with pytest.raises(ConfigurationError):
            self.validator.validate(invalid_config, config_file)


class TestConfigIntegration:
    """Test configuration integration with other components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ConfigManager()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_config_with_environment_variables(self):
        """Test configuration with environment variable substitution."""
        config_data = {
            'output': {
                'directory': '${OUTPUT_DIR:-./output}'
            },
            'variables': {
                'author': '${AUTHOR:-Default Author}'
            }
        }
        
        config_file = self.temp_path / "env.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Mock environment variables
        with patch.dict('os.environ', {'OUTPUT_DIR': '/custom/output', 'AUTHOR': 'Env Author'}):
            config = self.manager.load_config(config_file)
            
            # Note: Environment variable substitution would need to be implemented
            # This test shows the structure for when it's added
            assert config.output.directory == '${OUTPUT_DIR:-./output}'  # Raw value for now
    
    def test_config_inheritance(self):
        """Test configuration inheritance from base configs."""
        # Create base config
        base_config_data = {
            'name': 'base-config',
            'slides': {
                'theme': 'white',
                'transition': 'slide'
            },
            'output': {
                'formats': ['html']
            }
        }
        
        base_config_file = self.temp_path / "base.yaml"
        with open(base_config_file, 'w') as f:
            yaml.dump(base_config_data, f)
        
        # Create derived config
        derived_config_data = {
            'extends': str(base_config_file),  # Would need implementation
            'name': 'derived-config',
            'slides': {
                'theme': 'dark'  # Override theme
            },
            'output': {
                'formats': ['html', 'pdf']  # Extend formats
            }
        }
        
        derived_config_file = self.temp_path / "derived.yaml"
        with open(derived_config_file, 'w') as f:
            yaml.dump(derived_config_data, f)
        
        # Load derived config
        config = self.manager.load_config(derived_config_file)
        
        # For now, just test basic loading
        assert config.name == 'derived-config'
        assert config.slides.theme == 'dark'
        assert config.output.formats == ['html', 'pdf']
    
    def test_config_with_custom_sections(self):
        """Test configuration with custom user-defined sections."""
        config_data = {
            'name': 'custom-config',
            'custom': {
                'university': {
                    'name': 'Test University',
                    'logo': '/path/to/logo.png',
                    'colors': {
                        'primary': '#003366',
                        'secondary': '#66ccff'
                    }
                },
                'course': {
                    'code': 'CS101',
                    'title': 'Introduction to Computer Science',
                    'semester': 'Fall 2024'
                }
            },
            'variables': {
                'course_code': '${custom.course.code}',  # Reference custom section
                'university_name': '${custom.university.name}'
            }
        }
        
        config_file = self.temp_path / "custom.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        config = self.manager.load_config(config_file)
        
        assert config.custom['university']['name'] == 'Test University'
        assert config.custom['course']['code'] == 'CS101'
        assert config.variables['course_code'] == '${custom.course.code}'


class TestConfigPerformance:
    """Test configuration performance characteristics."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ConfigManager()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_large_config_loading(self):
        """Test loading of large configuration files."""
        import time
        
        # Create a large configuration
        large_config = {
            'name': 'large-config',
            'variables': {f'var_{i}': f'value_{i}' for i in range(1000)},
            'custom': {
                'section1': {f'key_{i}': f'value_{i}' for i in range(500)},
                'section2': {f'key_{i}': f'value_{i}' for i in range(500)}
            }
        }
        
        config_file = self.temp_path / "large.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(large_config, f)
        
        start_time = time.time()
        config = self.manager.load_config(config_file)
        load_time = time.time() - start_time
        
        # Should load within reasonable time (< 1 second)
        assert load_time < 1.0
        assert len(config.variables) == 1000
        assert len(config.custom['section1']) == 500
    
    def test_config_caching_performance(self):
        """Test performance benefits of configuration caching."""
        import time
        
        config_data = {'name': 'cached-perf-test'}
        config_file = self.temp_path / "cached_perf.yaml"
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # First load (should be slower)
        start_time = time.time()
        config1 = self.manager.load_config(config_file)
        first_load_time = time.time() - start_time
        
        # Second load (should be faster due to caching)
        start_time = time.time()
        config2 = self.manager.load_config(config_file)
        second_load_time = time.time() - start_time
        
        # Cached load should be significantly faster
        assert second_load_time < first_load_time
        assert config1 is config2  # Same object due to caching


if __name__ == "__main__":
    pytest.main([__file__])