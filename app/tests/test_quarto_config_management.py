"""
Tests for Quarto Configuration Management - Task 3.2 Implementation

Tests the advanced Quarto configuration management system including dynamic YAML
configuration generation, theme management, and project structure handling.
"""

import pytest
import tempfile
import shutil
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

from src.markdown_slides_generator.core.quarto_orchestrator import (
    QuartoThemeManager,
    QuartoConfigurationManager,
    QuartoOrchestrator
)
from src.markdown_slides_generator.themes.theme_manager import ThemeManager


class TestQuartoThemeManager:
    """Test the Quarto theme management system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.theme_manager = QuartoThemeManager(str(self.temp_dir))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_builtin_themes_available(self):
        """Test that built-in themes are available."""
        revealjs_themes = self.theme_manager.get_available_themes('revealjs')
        beamer_themes = self.theme_manager.get_available_themes('beamer')
        html_themes = self.theme_manager.get_available_themes('html')
        
        assert 'white' in revealjs_themes
        assert 'black' in revealjs_themes
        assert 'Madrid' in beamer_themes
        assert 'Berlin' in beamer_themes
        assert 'cosmo' in html_themes
        assert 'bootstrap' in html_themes
    
    def test_custom_themes_detection(self):
        """Test detection of custom themes."""
        # Create custom theme directories
        revealjs_dir = self.temp_dir / 'revealjs'
        revealjs_dir.mkdir()
        
        # Create custom theme files
        custom_theme = revealjs_dir / 'custom.css'
        custom_theme.write_text('.reveal { background: red; }')
        
        themes = self.theme_manager.get_available_themes('revealjs')
        
        assert 'custom' in themes
        assert 'white' in themes  # Built-in should still be there
    
    def test_theme_validation(self):
        """Test theme validation."""
        assert self.theme_manager.validate_theme('white', 'revealjs') is True
        assert self.theme_manager.validate_theme('Madrid', 'beamer') is True
        assert self.theme_manager.validate_theme('nonexistent', 'revealjs') is False
    
    def test_custom_theme_path(self):
        """Test getting path to custom theme."""
        # Create custom theme
        revealjs_dir = self.temp_dir / 'revealjs'
        revealjs_dir.mkdir()
        custom_theme = revealjs_dir / 'academic.css'
        custom_theme.write_text('.reveal { font-family: serif; }')
        
        # Built-in theme should return None
        assert self.theme_manager.get_theme_path('white', 'revealjs') is None
        
        # Custom theme should return path
        path = self.theme_manager.get_theme_path('academic', 'revealjs')
        assert path == str(custom_theme)
    
    def test_revealjs_theme_customization(self):
        """Test RevealJS theme customization."""
        customizations = {
            'colors': {'background': '#ffffff', 'text': '#000000'},
            'fonts': {'heading': 'Arial', 'body': 'Helvetica'},
            'layout': {'margin': '0.1'}
        }
        
        config = self.theme_manager.create_theme_customization(
            'white', customizations, 'revealjs'
        )
        
        assert config['theme'] == 'white'
        assert config['background'] == '#ffffff'
        assert config['text'] == '#000000'
        assert config['heading'] == 'Arial'
        assert config['margin'] == '0.1'
    
    def test_beamer_theme_customization(self):
        """Test Beamer theme customization."""
        customizations = {
            'colortheme': 'dolphin',
            'fonttheme': 'serif',
            'innertheme': 'circles',
            'outertheme': 'infolines'
        }
        
        config = self.theme_manager.create_theme_customization(
            'Madrid', customizations, 'beamer'
        )
        
        assert config['theme'] == 'Madrid'
        assert config['colortheme'] == 'dolphin'
        assert config['fonttheme'] == 'serif'
        assert config['innertheme'] == 'circles'
        assert config['outertheme'] == 'infolines'
    
    def test_html_theme_customization(self):
        """Test HTML theme customization."""
        customizations = {
            'css': ['custom.css', 'academic.css'],
            'scss': ['variables.scss']
        }
        
        config = self.theme_manager.create_theme_customization(
            'cosmo', customizations, 'html'
        )
        
        assert config['theme'] == 'cosmo'
        assert config['css'] == ['custom.css', 'academic.css']
        assert config['scss'] == ['variables.scss']


class TestQuartoConfigurationManager:
    """Test the Quarto configuration management system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_manager = QuartoConfigurationManager(str(self.temp_dir))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_slides_config_creation(self):
        """Test creation of slides configuration."""
        config = self.config_manager.create_slides_config(
            title="Test Presentation",
            format_type="revealjs",
            theme="white",
            author="John Doe",
            date="2024-01-01",
            institute="University"
        )
        
        assert config['title'] == "Test Presentation"
        assert config['author'] == "John Doe"
        assert config['date'] == "2024-01-01"
        assert config['institute'] == "University"
        assert 'revealjs' in config['format']
        assert config['format']['revealjs']['theme'] == 'white'
        assert config['editor'] == 'visual'
    
    def test_notes_config_creation(self):
        """Test creation of notes configuration."""
        config = self.config_manager.create_notes_config(
            title="Lecture Notes",
            format_type="pdf",
            academic_style=True,
            author="Professor Smith",
            bibliography="references.bib"
        )
        
        assert config['title'] == "Lecture Notes"
        assert config['author'] == "Professor Smith"
        assert config['bibliography'] == "references.bib"
        assert 'pdf' in config['format']
        assert config['format']['pdf']['documentclass'] == 'article'
        assert config['format']['pdf']['toc'] is True
        assert config['format']['pdf']['number-sections'] is True
    
    def test_academic_pdf_config(self):
        """Test academic PDF configuration."""
        config = self.config_manager._get_academic_format_config("pdf")
        
        assert config['documentclass'] == 'article'
        assert config['geometry'] == 'margin=1in'
        assert config['fontsize'] == '11pt'
        assert config['toc'] is True
        assert config['number-sections'] is True
        assert config['pdf-engine'] == 'xelatex'
        assert config['cite-method'] == 'biblatex'
        assert 'include-in-header' in config
    
    def test_academic_html_config(self):
        """Test academic HTML configuration."""
        config = self.config_manager._get_academic_format_config("html")
        
        assert config['theme'] == 'cosmo'
        assert config['toc'] is True
        assert config['toc-depth'] == 3
        assert config['number-sections'] is True
        assert config['code-fold'] is True
        assert config['code-tools'] is True
        assert config['anchor-sections'] is True
    
    def test_yaml_frontmatter_generation(self):
        """Test YAML frontmatter generation."""
        config = {
            'title': 'Test Document',
            'author': 'Test Author',
            'format': {
                'pdf': {
                    'toc': True
                }
            }
        }
        
        frontmatter = self.config_manager.generate_yaml_frontmatter(config)
        
        assert frontmatter.startswith('---\n')
        assert frontmatter.endswith('---\n\n')
        assert 'title: Test Document' in frontmatter
        assert 'author: Test Author' in frontmatter
        assert 'toc: true' in frontmatter
    
    def test_project_structure_creation(self):
        """Test creation of Quarto project structure."""
        project_name = "test_project"
        file_paths = self.config_manager.create_project_structure(project_name)
        
        project_dir = self.temp_dir / project_name
        
        # Check directories were created
        assert (project_dir / 'slides').exists()
        assert (project_dir / 'notes').exists()
        assert (project_dir / '_templates').exists()
        assert (project_dir / 'resources').exists()
        assert (project_dir / 'output').exists()
        
        # Check files were created
        assert (project_dir / '_quarto.yml').exists()
        assert (project_dir / '.gitignore').exists()
        assert (project_dir / 'README.md').exists()
        
        # Check file paths are returned
        assert 'project_config' in file_paths
        assert 'slides' in file_paths
        assert 'notes' in file_paths
    
    def test_project_config_creation(self):
        """Test _quarto.yml project configuration creation."""
        project_name = "academic_project"
        config_yaml = self.config_manager._create_project_config(project_name)
        
        config = yaml.safe_load(config_yaml)
        
        assert config['project']['type'] == 'default'
        assert config['project']['title'] == 'Academic Project'
        assert 'revealjs' in config['format']
        assert 'pdf' in config['format']
        assert 'html' in config['format']
        assert config['execute']['freeze'] == 'auto'
    
    def test_gitignore_creation(self):
        """Test .gitignore creation."""
        gitignore = self.config_manager._create_gitignore()
        
        assert '/.quarto/' in gitignore
        assert '/_site/' in gitignore
        assert '*.aux' in gitignore
        assert '__pycache__/' in gitignore
        assert '.DS_Store' in gitignore
    
    def test_readme_creation(self):
        """Test README.md creation."""
        readme = self.config_manager._create_readme("test_project")
        
        assert '# Test Project' in readme
        assert 'slides/' in readme
        assert 'notes/' in readme
        assert 'quarto render' in readme
    
    def test_project_config_loading(self):
        """Test loading project configuration."""
        # Create a test project first
        project_name = "config_test"
        self.config_manager.create_project_structure(project_name)
        
        # Load the configuration
        config = self.config_manager.load_project_config(
            str(self.temp_dir / project_name)
        )
        
        assert config['project']['type'] == 'default'
        assert 'format' in config
    
    def test_project_config_updating(self):
        """Test updating project configuration."""
        # Create a test project
        project_name = "update_test"
        self.config_manager.create_project_structure(project_name)
        project_path = str(self.temp_dir / project_name)
        
        # Update configuration
        updates = {
            'format': {
                'revealjs': {
                    'theme': 'dark',
                    'slide-number': False
                }
            }
        }
        
        success = self.config_manager.update_project_config(updates, project_path)
        assert success is True
        
        # Verify updates were applied
        updated_config = self.config_manager.load_project_config(project_path)
        assert updated_config['format']['revealjs']['theme'] == 'dark'
        assert updated_config['format']['revealjs']['slide-number'] is False
    
    def test_deep_merge(self):
        """Test deep merging of configuration dictionaries."""
        base = {
            'format': {
                'revealjs': {
                    'theme': 'white',
                    'slide-number': True
                },
                'pdf': {
                    'toc': True
                }
            }
        }
        
        updates = {
            'format': {
                'revealjs': {
                    'theme': 'dark'
                },
                'html': {
                    'theme': 'cosmo'
                }
            }
        }
        
        result = self.config_manager._deep_merge(base, updates)
        
        # Should preserve existing values not being updated
        assert result['format']['revealjs']['slide-number'] is True
        assert result['format']['pdf']['toc'] is True
        
        # Should apply updates
        assert result['format']['revealjs']['theme'] == 'dark'
        assert result['format']['html']['theme'] == 'cosmo'
    
    def test_latex_header_includes(self):
        """Test LaTeX header includes generation."""
        includes = self.config_manager._get_latex_header_includes()
        
        assert any('amsmath' in include for include in includes)
        assert any('graphicx' in include for include in includes)
        assert any('booktabs' in include for include in includes)
    
    def test_custom_latex_header(self):
        """Test custom LaTeX header file usage."""
        # Create templates directory and custom header
        templates_dir = self.temp_dir / '_templates'
        templates_dir.mkdir()
        header_file = templates_dir / 'header.tex'
        header_file.write_text('\\usepackage{custom}')
        
        # Update config manager to use this templates directory
        self.config_manager.templates_dir = templates_dir
        
        includes = self.config_manager._get_latex_header_includes()
        
        assert str(header_file) in includes


class TestQuartoOrchestratorConfigIntegration:
    """Test integration of configuration management with QuartoOrchestrator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    @patch('src.markdown_slides_generator.core.quarto_orchestrator.QuartoExecutor')
    def test_enhanced_config_creation(self, mock_executor_class):
        """Test enhanced configuration creation in orchestrator."""
        orchestrator = QuartoOrchestrator()
        
        # Test slides configuration
        slides_config = {
            'slides': True,
            'title': 'Advanced Presentation',
            'format': 'revealjs',
            'theme': 'dark',
            'author': 'Dr. Smith',
            'institute': 'University'
        }
        
        yaml_config = orchestrator.create_quarto_config(slides_config)
        
        assert 'title: Advanced Presentation' in yaml_config
        assert 'author: Dr. Smith' in yaml_config
        assert 'institute: University' in yaml_config
        assert 'revealjs:' in yaml_config
    
    @patch('src.markdown_slides_generator.core.quarto_orchestrator.QuartoExecutor')
    def test_notes_config_creation(self, mock_executor_class):
        """Test notes configuration creation in orchestrator."""
        orchestrator = QuartoOrchestrator()
        
        # Test notes configuration
        notes_config = {
            'notes': True,
            'title': 'Comprehensive Notes',
            'format': 'pdf',
            'academic_style': True,
            'author': 'Professor Jones',
            'bibliography': 'refs.bib'
        }
        
        yaml_config = orchestrator.create_quarto_config(notes_config)
        
        assert 'title: Comprehensive Notes' in yaml_config
        assert 'author: Professor Jones' in yaml_config
        assert 'bibliography: refs.bib' in yaml_config
        assert 'pdf:' in yaml_config
        assert 'documentclass: article' in yaml_config
    
    @patch('src.markdown_slides_generator.core.quarto_orchestrator.QuartoExecutor')
    def test_project_creation(self, mock_executor_class):
        """Test project creation through orchestrator."""
        orchestrator = QuartoOrchestrator()
        
        file_paths = orchestrator.create_project(
            "test_lecture_series",
            str(self.temp_dir)
        )
        
        assert 'project_config' in file_paths
        assert 'slides' in file_paths
        assert 'notes' in file_paths
        
        # Verify project was actually created
        project_dir = self.temp_dir / "test_lecture_series"
        assert project_dir.exists()
        assert (project_dir / '_quarto.yml').exists()
    
    @patch('src.markdown_slides_generator.core.quarto_orchestrator.QuartoExecutor')
    def test_theme_manager_access(self, mock_executor_class):
        """Test accessing theme manager through orchestrator."""
        orchestrator = QuartoOrchestrator()
        
        theme_manager = orchestrator.get_theme_manager()
        
        assert isinstance(theme_manager, ThemeManager)
        # Test that we can list themes (ThemeManager has list_themes method)
        themes = theme_manager.list_themes()
        assert isinstance(themes, dict)
        assert len(themes) > 0
    
    @patch('src.markdown_slides_generator.core.quarto_orchestrator.QuartoExecutor')
    def test_config_manager_access(self, mock_executor_class):
        """Test accessing configuration manager through orchestrator."""
        orchestrator = QuartoOrchestrator()
        
        config_manager = orchestrator.get_configuration_manager(str(self.temp_dir))
        
        assert isinstance(config_manager, QuartoConfigurationManager)
        assert config_manager.project_dir == Path(self.temp_dir)


class TestConfigurationEdgeCases:
    """Test edge cases and error handling in configuration management."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_manager = QuartoConfigurationManager(str(self.temp_dir))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_nonexistent_project_config_loading(self):
        """Test loading configuration from nonexistent project."""
        config = self.config_manager.load_project_config("/nonexistent/path")
        assert config == {}
    
    def test_invalid_yaml_config_loading(self):
        """Test loading invalid YAML configuration."""
        # Create invalid YAML file
        invalid_config = self.temp_dir / '_quarto.yml'
        invalid_config.write_text('invalid: yaml: content: [')
        
        config = self.config_manager.load_project_config(str(self.temp_dir))
        assert config == {}
    
    def test_config_update_nonexistent_project(self):
        """Test updating configuration for nonexistent project."""
        success = self.config_manager.update_project_config(
            {'format': {'pdf': {'toc': True}}},
            "/nonexistent/path"
        )
        assert success is False
    
    def test_empty_config_creation(self):
        """Test creating configuration with minimal parameters."""
        config = self.config_manager.create_slides_config("Minimal")
        
        assert config['title'] == "Minimal"
        assert 'format' in config
        assert 'editor' in config
    
    def test_custom_options_override(self):
        """Test that custom options properly override defaults."""
        custom_options = {
            'theme': 'custom_theme',
            'slide-number': False,
            'new_option': 'custom_value'
        }
        
        config = self.config_manager.create_slides_config(
            "Custom Test",
            custom_options=custom_options
        )
        
        format_config = config['format']['revealjs']
        assert format_config['theme'] == 'custom_theme'
        assert format_config['slide-number'] is False
        assert format_config['new_option'] == 'custom_value'