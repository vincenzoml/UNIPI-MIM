"""
Tests for the theme management system.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from markdown_slides_generator.themes.theme_manager import (
    ThemeManager, AcademicTheme, ThemeStyle, ColorScheme, 
    BrandingConfig, TypographyConfig
)
from markdown_slides_generator.utils.exceptions import OutputError


class TestThemeManager:
    """Test cases for ThemeManager."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.theme_manager = ThemeManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test theme manager initialization."""
        assert self.theme_manager is not None
        assert self.theme_manager.themes_dir.exists()
        
        # Check built-in themes are loaded
        themes = self.theme_manager.list_themes()
        assert len(themes) > 0
        assert "academic-minimal" in themes
        assert "academic-modern" in themes
        assert "academic-technical" in themes
    
    def test_get_builtin_theme(self):
        """Test getting built-in themes."""
        theme = self.theme_manager.get_theme("academic-minimal")
        
        assert isinstance(theme, AcademicTheme)
        assert theme.name == "academic-minimal"
        assert theme.display_name == "Academic Minimal"
        assert theme.style == ThemeStyle.MINIMAL
        assert theme.color_scheme == ColorScheme.LIGHT
        assert theme.background_color == "#ffffff"
        assert theme.text_color == "#333333"
    
    def test_get_nonexistent_theme(self):
        """Test getting non-existent theme raises error."""
        with pytest.raises(OutputError, match="Theme 'nonexistent' not found"):
            self.theme_manager.get_theme("nonexistent")
    
    def test_list_themes(self):
        """Test listing all themes."""
        themes = self.theme_manager.list_themes()
        
        assert isinstance(themes, dict)
        assert len(themes) >= 5  # At least 5 built-in themes
        
        # Check theme info structure
        for theme_name, theme_info in themes.items():
            assert "display_name" in theme_info
            assert "description" in theme_info
            assert "style" in theme_info
            assert "color_scheme" in theme_info
            assert "type" in theme_info
    
    def test_create_custom_theme(self):
        """Test creating custom theme."""
        customizations = {
            "background_color": "#f0f0f0",
            "accent_color": "#ff6b6b",
            "description": "Custom test theme"
        }
        
        custom_theme = self.theme_manager.create_custom_theme(
            "test-custom",
            "academic-minimal",
            customizations
        )
        
        assert custom_theme.name == "test-custom"
        assert custom_theme.background_color == "#f0f0f0"
        assert custom_theme.accent_color == "#ff6b6b"
        assert custom_theme.description == "Custom test theme"
        
        # Verify it's in the list
        themes = self.theme_manager.list_themes()
        assert "test-custom" in themes
        assert themes["test-custom"]["type"] == "custom"
    
    def test_generate_reveal_css(self):
        """Test generating reveal.js CSS."""
        theme = self.theme_manager.get_theme("academic-minimal")
        css = self.theme_manager.generate_reveal_css(theme)
        
        assert isinstance(css, str)
        assert len(css) > 0
        
        # Check for key CSS elements
        assert ":root {" in css
        assert "--r-background-color:" in css
        assert "--r-main-color:" in css
        assert ".reveal" in css
        assert "font-family:" in css
    
    def test_generate_css_with_branding(self):
        """Test generating CSS with branding."""
        theme = self.theme_manager.get_theme("academic-minimal")
        theme.branding.logo_path = "/path/to/logo.png"
        theme.branding.institution_name = "Test University"
        theme.branding.footer_text = "Test Footer"
        
        css = self.theme_manager.generate_reveal_css(theme)
        
        assert "background-image: url('/path/to/logo.png')" in css
        assert "content: 'Test Footer'" in css
    
    def test_export_theme_css(self):
        """Test exporting theme as CSS file."""
        output_file = Path(self.temp_dir) / "test-theme.css"
        
        result_path = self.theme_manager.export_theme_css(
            "academic-minimal",
            str(output_file)
        )
        
        assert Path(result_path).exists()
        assert Path(result_path) == output_file
        
        # Check file content
        with open(result_path, 'r') as f:
            content = f.read()
        
        assert len(content) > 0
        assert ":root {" in content
    
    def test_theme_preview_html(self):
        """Test generating theme preview HTML."""
        html = self.theme_manager.get_theme_preview_html("academic-minimal")
        
        assert isinstance(html, str)
        assert len(html) > 0
        assert "<!DOCTYPE html>" in html
        assert "Academic Minimal" in html
        assert "Theme Preview:" in html
        assert "<style>" in html
    
    def test_typography_config(self):
        """Test typography configuration."""
        typography = TypographyConfig(
            heading_font="Custom Font",
            body_font="Another Font",
            font_size_base="24px"
        )
        
        assert typography.heading_font == "Custom Font"
        assert typography.body_font == "Another Font"
        assert typography.font_size_base == "24px"
        assert typography.line_height == "1.3"  # Default value
    
    def test_branding_config(self):
        """Test branding configuration."""
        branding = BrandingConfig(
            logo_path="/path/to/logo.png",
            logo_position="top-left",
            institution_name="Test University",
            institution_color="#0066cc"
        )
        
        assert branding.logo_path == "/path/to/logo.png"
        assert branding.logo_position == "top-left"
        assert branding.institution_name == "Test University"
        assert branding.institution_color == "#0066cc"
    
    def test_academic_theme_creation(self):
        """Test creating AcademicTheme object."""
        theme = AcademicTheme(
            name="test-theme",
            display_name="Test Theme",
            style=ThemeStyle.MODERN,
            color_scheme=ColorScheme.BLUE,
            description="A test theme"
        )
        
        assert theme.name == "test-theme"
        assert theme.style == ThemeStyle.MODERN
        assert theme.color_scheme == ColorScheme.BLUE
        assert isinstance(theme.typography, TypographyConfig)
        assert isinstance(theme.branding, BrandingConfig)
    
    def test_theme_styles_and_colors(self):
        """Test theme style and color scheme enums."""
        # Test all theme styles
        styles = [ThemeStyle.MINIMAL, ThemeStyle.CLASSIC, ThemeStyle.MODERN, 
                 ThemeStyle.TECHNICAL, ThemeStyle.ELEGANT]
        
        for style in styles:
            assert isinstance(style.value, str)
        
        # Test all color schemes
        colors = [ColorScheme.LIGHT, ColorScheme.DARK, ColorScheme.BLUE,
                 ColorScheme.GREEN, ColorScheme.PURPLE, ColorScheme.NEUTRAL]
        
        for color in colors:
            assert isinstance(color.value, str)
    
    def test_custom_theme_persistence(self):
        """Test that custom themes are saved and loaded."""
        # Create custom theme
        custom_theme = self.theme_manager.create_custom_theme(
            "persistent-theme",
            "academic-minimal",
            {"accent_color": "#123456"}
        )
        
        # Create new theme manager instance (simulates restart)
        new_manager = ThemeManager(self.temp_dir)
        
        # Check if custom theme is loaded
        themes = new_manager.list_themes()
        assert "persistent-theme" in themes
        
        # Get the theme and verify customization
        loaded_theme = new_manager.get_theme("persistent-theme")
        assert loaded_theme.accent_color == "#123456"


class TestThemeCSS:
    """Test cases for CSS generation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.theme_manager = ThemeManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_css_variables_generation(self):
        """Test CSS custom properties generation."""
        theme = self.theme_manager.get_theme("academic-modern")
        css = self.theme_manager.generate_reveal_css(theme)
        
        # Check for CSS variables
        assert "--r-background-color: #ffffff;" in css
        assert "--r-main-color: #2d3748;" in css
        assert "--r-heading-color: #1a202c;" in css
        assert "--r-accent-color: #3182ce;" in css
    
    def test_font_imports_generation(self):
        """Test font import generation."""
        theme = self.theme_manager.get_theme("academic-modern")
        css = self.theme_manager.generate_reveal_css(theme)
        
        # Check for font imports
        assert "@import url('https://fonts.googleapis.com/css2?family=Inter:" in css
    
    def test_academic_styles_generation(self):
        """Test academic-specific styles generation."""
        theme = self.theme_manager.get_theme("academic-minimal")
        css = self.theme_manager.generate_reveal_css(theme)
        
        # Check for academic-specific classes
        assert ".reveal .title-slide h1" in css
        assert ".reveal .slide-number" in css
        assert ".reveal .MathJax" in css
        assert ".reveal table" in css
        assert ".reveal .highlight" in css
    
    def test_different_theme_css_differences(self):
        """Test that different themes generate different CSS."""
        minimal_css = self.theme_manager.generate_reveal_css(
            self.theme_manager.get_theme("academic-minimal")
        )
        modern_css = self.theme_manager.generate_reveal_css(
            self.theme_manager.get_theme("academic-modern")
        )
        
        # Should be different
        assert minimal_css != modern_css
        
        # But both should have basic structure
        for css in [minimal_css, modern_css]:
            assert ":root {" in css
            assert ".reveal" in css
            assert "font-family:" in css