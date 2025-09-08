"""
Professional academic theme management system.

Provides custom reveal.js themes optimized for academic presentations with
clean, minimalist designs and excellent typography.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

from ..utils.logger import get_logger
from ..utils.exceptions import handle_exception, OutputError

logger = get_logger(__name__)


class ThemeStyle(Enum):
    """Academic presentation styles."""
    MINIMAL = "minimal"
    CLASSIC = "classic"
    MODERN = "modern"
    TECHNICAL = "technical"
    ELEGANT = "elegant"


class ColorScheme(Enum):
    """Color schemes for academic themes."""
    LIGHT = "light"
    DARK = "dark"
    BLUE = "blue"
    GREEN = "green"
    PURPLE = "purple"
    NEUTRAL = "neutral"


@dataclass
class BrandingConfig:
    """Configuration for institutional branding."""
    logo_path: Optional[str] = None
    logo_position: str = "top-right"  # top-left, top-right, bottom-left, bottom-right
    logo_size: str = "80px"
    institution_name: Optional[str] = None
    institution_color: Optional[str] = None
    footer_text: Optional[str] = None
    header_text: Optional[str] = None


@dataclass
class TypographyConfig:
    """Typography configuration for themes."""
    heading_font: str = "Source Sans Pro"
    body_font: str = "Source Sans Pro"
    code_font: str = "Source Code Pro"
    font_size_base: str = "32px"
    font_size_h1: str = "2.5em"
    font_size_h2: str = "1.6em"
    font_size_h3: str = "1.3em"
    line_height: str = "1.3"
    letter_spacing: str = "normal"


@dataclass
class AcademicTheme:
    """Complete academic theme configuration."""
    name: str
    display_name: str
    style: ThemeStyle
    color_scheme: ColorScheme
    description: str
    
    # Core colors
    background_color: str = "#ffffff"
    text_color: str = "#222222"
    heading_color: str = "#1a1a1a"
    accent_color: str = "#2e86ab"
    secondary_color: str = "#a23b72"
    
    # Typography
    typography: TypographyConfig = None
    
    # Branding
    branding: BrandingConfig = None
    
    # Reveal.js specific settings
    transition: str = "slide"
    transition_speed: str = "default"
    background_transition: str = "fade"
    
    # Academic-specific features
    show_slide_numbers: bool = True
    show_progress: bool = True
    enable_chalkboard: bool = True
    enable_menu: bool = True
    enable_overview: bool = True
    
    # Custom CSS overrides
    custom_css: Optional[str] = None
    
    def __post_init__(self):
        if self.typography is None:
            self.typography = TypographyConfig()
        if self.branding is None:
            self.branding = BrandingConfig()


class ThemeManager:
    """
    Professional theme management system for academic presentations.
    
    Manages built-in themes, custom themes, and theme customizations
    with support for institutional branding and multiple academic styles.
    """
    
    def __init__(self, themes_dir: Optional[str] = None):
        """
        Initialize theme manager.
        
        Args:
            themes_dir: Optional custom themes directory
        """
        self.themes_dir = Path(themes_dir) if themes_dir else self._get_default_themes_dir()
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize built-in themes
        self._builtin_themes = self._create_builtin_themes()
        self._custom_themes: Dict[str, AcademicTheme] = {}
        
        # Load existing custom themes
        self._load_custom_themes()
        
        logger.info(f"Theme manager initialized with {len(self._builtin_themes)} built-in themes")
    
    def _get_default_themes_dir(self) -> Path:
        """Get default themes directory."""
        return Path(__file__).parent / "assets" / "themes"
    
    def _create_builtin_themes(self) -> Dict[str, AcademicTheme]:
        """Create built-in academic themes."""
        themes = {}
        
        # Academic Minimal - Clean and simple
        themes["academic-minimal"] = AcademicTheme(
            name="academic-minimal",
            display_name="Academic Minimal",
            style=ThemeStyle.MINIMAL,
            color_scheme=ColorScheme.LIGHT,
            description="Clean, minimal design perfect for academic presentations",
            background_color="#ffffff",
            text_color="#333333",
            heading_color="#1a1a1a",
            accent_color="#0066cc",
            secondary_color="#666666",
            typography=TypographyConfig(
                heading_font="Source Sans Pro",
                body_font="Source Sans Pro",
                font_size_base="28px",
                line_height="1.4"
            )
        )
        
        # Academic Classic - Traditional academic style
        themes["academic-classic"] = AcademicTheme(
            name="academic-classic",
            display_name="Academic Classic",
            style=ThemeStyle.CLASSIC,
            color_scheme=ColorScheme.NEUTRAL,
            description="Traditional academic style with serif typography",
            background_color="#fefefe",
            text_color="#2c2c2c",
            heading_color="#1a1a1a",
            accent_color="#8b0000",
            secondary_color="#4a4a4a",
            typography=TypographyConfig(
                heading_font="Crimson Text",
                body_font="Crimson Text",
                code_font="Source Code Pro",
                font_size_base="30px",
                line_height="1.5"
            )
        )
        
        # Academic Modern - Contemporary design
        themes["academic-modern"] = AcademicTheme(
            name="academic-modern",
            display_name="Academic Modern",
            style=ThemeStyle.MODERN,
            color_scheme=ColorScheme.BLUE,
            description="Modern academic design with vibrant accents",
            background_color="#ffffff",
            text_color="#2d3748",
            heading_color="#1a202c",
            accent_color="#3182ce",
            secondary_color="#805ad5",
            typography=TypographyConfig(
                heading_font="Inter",
                body_font="Inter",
                font_size_base="30px",
                line_height="1.4"
            ),
            transition="convex",
            background_transition="zoom"
        )
        
        # Academic Technical - For STEM presentations
        themes["academic-technical"] = AcademicTheme(
            name="academic-technical",
            display_name="Academic Technical",
            style=ThemeStyle.TECHNICAL,
            color_scheme=ColorScheme.DARK,
            description="Technical theme optimized for STEM presentations",
            background_color="#1a1a1a",
            text_color="#e2e8f0",
            heading_color="#ffffff",
            accent_color="#00d4aa",
            secondary_color="#ff6b6b",
            typography=TypographyConfig(
                heading_font="Roboto",
                body_font="Roboto",
                code_font="JetBrains Mono",
                font_size_base="28px",
                line_height="1.3"
            ),
            show_slide_numbers=True,
            enable_chalkboard=True
        )
        
        # Academic Elegant - Sophisticated design
        themes["academic-elegant"] = AcademicTheme(
            name="academic-elegant",
            display_name="Academic Elegant",
            style=ThemeStyle.ELEGANT,
            color_scheme=ColorScheme.PURPLE,
            description="Elegant design for high-profile academic presentations",
            background_color="#fafafa",
            text_color="#2d3748",
            heading_color="#1a202c",
            accent_color="#805ad5",
            secondary_color="#d69e2e",
            typography=TypographyConfig(
                heading_font="Playfair Display",
                body_font="Source Sans Pro",
                font_size_base="30px",
                line_height="1.4"
            ),
            transition="fade",
            background_transition="fade"
        )
        
        return themes
    
    @handle_exception
    def get_theme(self, theme_name: str) -> AcademicTheme:
        """
        Get theme by name.
        
        Args:
            theme_name: Name of the theme
            
        Returns:
            AcademicTheme object
            
        Raises:
            OutputError: If theme not found
        """
        # Check built-in themes first
        if theme_name in self._builtin_themes:
            return self._builtin_themes[theme_name]
        
        # Check custom themes
        if theme_name in self._custom_themes:
            return self._custom_themes[theme_name]
        
        raise OutputError(f"Theme '{theme_name}' not found")
    
    def list_themes(self) -> Dict[str, Dict[str, str]]:
        """
        List all available themes.
        
        Returns:
            Dictionary with theme information
        """
        themes_info = {}
        
        # Built-in themes
        for name, theme in self._builtin_themes.items():
            themes_info[name] = {
                'display_name': theme.display_name,
                'description': theme.description,
                'style': theme.style.value,
                'color_scheme': theme.color_scheme.value,
                'type': 'built-in'
            }
        
        # Custom themes
        for name, theme in self._custom_themes.items():
            themes_info[name] = {
                'display_name': theme.display_name,
                'description': theme.description,
                'style': theme.style.value,
                'color_scheme': theme.color_scheme.value,
                'type': 'custom'
            }
        
        return themes_info
    
    @handle_exception
    def create_custom_theme(
        self,
        name: str,
        base_theme: str = "academic-minimal",
        customizations: Optional[Dict[str, Any]] = None
    ) -> AcademicTheme:
        """
        Create a custom theme based on an existing theme.
        
        Args:
            name: Name for the new theme
            base_theme: Base theme to customize
            customizations: Dictionary of customizations
            
        Returns:
            New AcademicTheme object
            
        Raises:
            OutputError: If base theme not found or creation fails
        """
        logger.info(f"Creating custom theme '{name}' based on '{base_theme}'")
        
        # Get base theme
        base = self.get_theme(base_theme)
        
        # Create copy for customization
        theme_dict = asdict(base)
        theme_dict['name'] = name
        theme_dict['display_name'] = name.replace('-', ' ').title()
        
        # Apply customizations
        if customizations:
            self._apply_customizations(theme_dict, customizations)
        
        # Reconstruct nested dataclasses
        if 'typography' in theme_dict and isinstance(theme_dict['typography'], dict):
            theme_dict['typography'] = TypographyConfig(**theme_dict['typography'])
        if 'branding' in theme_dict and isinstance(theme_dict['branding'], dict):
            theme_dict['branding'] = BrandingConfig(**theme_dict['branding'])
        
        # Create new theme object
        custom_theme = AcademicTheme(**theme_dict)
        
        # Save custom theme
        self._save_custom_theme(custom_theme)
        self._custom_themes[name] = custom_theme
        
        logger.info(f"Created custom theme '{name}'")
        return custom_theme
    
    def _apply_customizations(self, theme_dict: Dict[str, Any], customizations: Dict[str, Any]):
        """Apply customizations to theme dictionary."""
        for key, value in customizations.items():
            if key in theme_dict:
                if isinstance(theme_dict[key], dict) and isinstance(value, dict):
                    theme_dict[key].update(value)
                else:
                    theme_dict[key] = value
            else:
                # Add new key if it doesn't exist
                theme_dict[key] = value
    
    @handle_exception
    def generate_reveal_css(self, theme: AcademicTheme) -> str:
        """
        Generate reveal.js CSS for the theme.
        
        Args:
            theme: AcademicTheme to generate CSS for
            
        Returns:
            CSS string for reveal.js
        """
        logger.debug(f"Generating reveal.js CSS for theme '{theme.name}'")
        
        css_parts = []
        
        # Import fonts
        css_parts.append(self._generate_font_imports(theme.typography))
        
        # Root variables
        css_parts.append(self._generate_css_variables(theme))
        
        # Base styles
        css_parts.append(self._generate_base_styles(theme))
        
        # Typography styles
        css_parts.append(self._generate_typography_styles(theme))
        
        # Academic-specific styles
        css_parts.append(self._generate_academic_styles(theme))
        
        # Branding styles
        if theme.branding.logo_path or theme.branding.institution_name:
            css_parts.append(self._generate_branding_styles(theme))
        
        # Custom CSS
        if theme.custom_css:
            css_parts.append(theme.custom_css)
        
        return "\n\n".join(css_parts)
    
    def _generate_font_imports(self, typography: TypographyConfig) -> str:
        """Generate font import statements."""
        fonts = set([typography.heading_font, typography.body_font, typography.code_font])
        imports = []
        
        for font in fonts:
            if font in ["Source Sans Pro", "Source Code Pro"]:
                imports.append(f"@import url('https://fonts.googleapis.com/css2?family={font.replace(' ', '+')}:wght@300;400;600;700&display=swap');")
            elif font == "Inter":
                imports.append("@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');")
            elif font == "Crimson Text":
                imports.append("@import url('https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');")
            elif font == "Roboto":
                imports.append("@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');")
            elif font == "Playfair Display":
                imports.append("@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&display=swap');")
            elif font == "JetBrains Mono":
                imports.append("@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500&display=swap');")
        
        return "\n".join(imports)
    
    def _generate_css_variables(self, theme: AcademicTheme) -> str:
        """Generate CSS custom properties."""
        return f"""
:root {{
  --r-background-color: {theme.background_color};
  --r-main-color: {theme.text_color};
  --r-heading-color: {theme.heading_color};
  --r-accent-color: {theme.accent_color};
  --r-secondary-color: {theme.secondary_color};
  
  --r-main-font: '{theme.typography.body_font}', sans-serif;
  --r-heading-font: '{theme.typography.heading_font}', sans-serif;
  --r-code-font: '{theme.typography.code_font}', monospace;
  
  --r-main-font-size: {theme.typography.font_size_base};
  --r-heading1-size: {theme.typography.font_size_h1};
  --r-heading2-size: {theme.typography.font_size_h2};
  --r-heading3-size: {theme.typography.font_size_h3};
  --r-line-height: {theme.typography.line_height};
  
  --r-block-margin: 20px;
  --r-heading-margin: 0 0 20px 0;
  --r-heading-line-height: 1.2;
  --r-heading-letter-spacing: {theme.typography.letter_spacing};
  --r-heading-text-transform: none;
  --r-heading-text-shadow: none;
  --r-heading-font-weight: 600;
}}"""
    
    def _generate_base_styles(self, theme: AcademicTheme) -> str:
        """Generate base reveal.js styles."""
        return f"""
.reveal {{
  font-family: var(--r-main-font);
  font-size: var(--r-main-font-size);
  font-weight: normal;
  color: var(--r-main-color);
}}

.reveal .slides section,
.reveal .slides section > section {{
  line-height: var(--r-line-height);
  font-weight: inherit;
}}

.reveal .slides {{
  text-align: left;
}}

.reveal .slides section {{
  padding: 40px;
  box-sizing: border-box;
}}

.reveal h1, .reveal h2, .reveal h3, .reveal h4, .reveal h5, .reveal h6 {{
  margin: var(--r-heading-margin);
  color: var(--r-heading-color);
  font-family: var(--r-heading-font);
  font-weight: var(--r-heading-font-weight);
  line-height: var(--r-heading-line-height);
  letter-spacing: var(--r-heading-letter-spacing);
  text-transform: var(--r-heading-text-transform);
  text-shadow: var(--r-heading-text-shadow);
  word-wrap: break-word;
}}

.reveal h1 {{ font-size: var(--r-heading1-size); }}
.reveal h2 {{ font-size: var(--r-heading2-size); }}
.reveal h3 {{ font-size: var(--r-heading3-size); }}"""
    
    def _generate_typography_styles(self, theme: AcademicTheme) -> str:
        """Generate typography-specific styles."""
        return f"""
.reveal p {{
  margin: var(--r-block-margin) 0;
  line-height: var(--r-line-height);
}}

.reveal ul, .reveal ol {{
  display: block;
  margin-left: 1em;
}}

.reveal ul li, .reveal ol li {{
  margin-bottom: 0.5em;
}}

.reveal blockquote {{
  display: block;
  position: relative;
  width: 70%;
  margin: var(--r-block-margin) auto;
  padding: 5px;
  font-style: italic;
  background: rgba(255, 255, 255, 0.05);
  box-shadow: 0px 0px 2px rgba(0, 0, 0, 0.2);
  border-left: 4px solid var(--r-accent-color);
}}

.reveal code {{
  font-family: var(--r-code-font);
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 3px;
}}

.reveal pre {{
  display: block;
  position: relative;
  width: 90%;
  margin: var(--r-block-margin) auto;
  text-align: left;
  font-size: 0.8em;
  font-family: var(--r-code-font);
  line-height: 1.2em;
  word-wrap: break-word;
  box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.15);
  background: #f8f8f8;
  border-radius: 5px;
  padding: 20px;
}}

.reveal pre code {{
  display: block;
  padding: 0;
  overflow: auto;
  max-height: 400px;
  word-wrap: normal;
  background: transparent;
}}"""
    
    def _generate_academic_styles(self, theme: AcademicTheme) -> str:
        """Generate academic-specific styles."""
        return f"""
/* Academic-specific enhancements */
.reveal .title-slide h1 {{
  font-size: 2.2em;
  margin-bottom: 0.5em;
  text-align: center;
}}

.reveal .title-slide .author {{
  font-size: 1.2em;
  margin-bottom: 0.3em;
  text-align: center;
  color: var(--r-secondary-color);
}}

.reveal .title-slide .date {{
  font-size: 1em;
  text-align: center;
  color: var(--r-secondary-color);
}}

.reveal .slide-number {{
  color: var(--r-secondary-color);
  background-color: transparent;
  font-size: 0.8em;
}}

.reveal .progress {{
  color: var(--r-accent-color);
}}

/* Math and equations */
.reveal .MathJax {{
  font-size: 1em !important;
}}

/* Tables */
.reveal table {{
  margin: auto;
  border-collapse: collapse;
  border-spacing: 0;
}}

.reveal table th {{
  font-weight: bold;
  background-color: var(--r-accent-color);
  color: white;
  padding: 0.5em;
}}

.reveal table td {{
  text-align: left;
  padding: 0.4em;
  border-bottom: 1px solid #ddd;
}}

/* Emphasis and highlighting */
.reveal .highlight {{
  background-color: var(--r-accent-color);
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
}}

.reveal .alert {{
  color: #d32f2f;
  font-weight: bold;
}}

.reveal .success {{
  color: #388e3c;
  font-weight: bold;
}}"""
    
    def _generate_branding_styles(self, theme: AcademicTheme) -> str:
        """Generate branding and logo styles."""
        styles = []
        
        if theme.branding.logo_path:
            position_styles = {
                "top-left": "top: 20px; left: 20px;",
                "top-right": "top: 20px; right: 20px;",
                "bottom-left": "bottom: 20px; left: 20px;",
                "bottom-right": "bottom: 20px; right: 20px;"
            }
            
            position = position_styles.get(theme.branding.logo_position, position_styles["top-right"])
            
            styles.append(f"""
.reveal .slide-background::after {{
  content: '';
  position: absolute;
  {position}
  width: {theme.branding.logo_size};
  height: {theme.branding.logo_size};
  background-image: url('{theme.branding.logo_path}');
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  z-index: 1000;
}}""")
        
        if theme.branding.footer_text:
            styles.append(f"""
.reveal .slide-background::before {{
  content: '{theme.branding.footer_text}';
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.7em;
  color: var(--r-secondary-color);
  z-index: 1000;
}}""")
        
        return "\n".join(styles)
    
    def _load_custom_themes(self):
        """Load custom themes from disk."""
        custom_themes_file = self.themes_dir / "custom_themes.json"
        
        if not custom_themes_file.exists():
            return
        
        try:
            with open(custom_themes_file, 'r', encoding='utf-8') as f:
                themes_data = json.load(f)
            
            for theme_data in themes_data:
                # Convert enum strings back to enums
                if 'style' in theme_data and isinstance(theme_data['style'], str):
                    theme_data['style'] = ThemeStyle(theme_data['style'])
                if 'color_scheme' in theme_data and isinstance(theme_data['color_scheme'], str):
                    theme_data['color_scheme'] = ColorScheme(theme_data['color_scheme'])
                
                # Handle nested dataclasses
                if 'typography' in theme_data and isinstance(theme_data['typography'], dict):
                    theme_data['typography'] = TypographyConfig(**theme_data['typography'])
                if 'branding' in theme_data and isinstance(theme_data['branding'], dict):
                    theme_data['branding'] = BrandingConfig(**theme_data['branding'])
                
                theme = AcademicTheme(**theme_data)
                self._custom_themes[theme.name] = theme
            
            logger.info(f"Loaded {len(self._custom_themes)} custom themes")
            
        except Exception as e:
            logger.error(f"Error loading custom themes: {e}")
    
    def _save_custom_theme(self, theme: AcademicTheme):
        """Save custom theme to disk."""
        custom_themes_file = self.themes_dir / "custom_themes.json"
        
        try:
            # Load existing themes
            themes_data = []
            if custom_themes_file.exists():
                with open(custom_themes_file, 'r', encoding='utf-8') as f:
                    themes_data = json.load(f)
            
            # Add or update theme
            theme_dict = asdict(theme)
            
            # Convert enums to their values for JSON serialization
            if 'style' in theme_dict and hasattr(theme_dict['style'], 'value'):
                theme_dict['style'] = theme_dict['style'].value
            if 'color_scheme' in theme_dict and hasattr(theme_dict['color_scheme'], 'value'):
                theme_dict['color_scheme'] = theme_dict['color_scheme'].value
            
            themes_data = [t for t in themes_data if t['name'] != theme.name]
            themes_data.append(theme_dict)
            
            # Save back to file
            with open(custom_themes_file, 'w', encoding='utf-8') as f:
                json.dump(themes_data, f, indent=2, default=str)
            
            logger.debug(f"Saved custom theme '{theme.name}'")
            
        except Exception as e:
            logger.error(f"Error saving custom theme: {e}")
    
    @handle_exception
    def export_theme_css(self, theme_name: str, output_path: str) -> str:
        """
        Export theme as CSS file.
        
        Args:
            theme_name: Name of theme to export
            output_path: Path to save CSS file
            
        Returns:
            Path to exported CSS file
            
        Raises:
            OutputError: If export fails
        """
        theme = self.get_theme(theme_name)
        css_content = self.generate_reveal_css(theme)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        logger.info(f"Exported theme '{theme_name}' to {output_file}")
        return str(output_file)
    
    def get_theme_preview_html(self, theme_name: str) -> str:
        """
        Generate HTML preview for a theme.
        
        Args:
            theme_name: Name of theme to preview
            
        Returns:
            HTML string with theme preview
        """
        theme = self.get_theme(theme_name)
        css = self.generate_reveal_css(theme)
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{theme.display_name} Preview</title>
    <style>
        {css}
        body {{ margin: 0; padding: 20px; background: var(--r-background-color); }}
        .preview {{ max-width: 800px; margin: 0 auto; }}
    </style>
</head>
<body>
    <div class="preview reveal">
        <h1>Theme Preview: {theme.display_name}</h1>
        <p>{theme.description}</p>
        
        <h2>Typography Examples</h2>
        <p>This is regular paragraph text demonstrating the body font and line height.</p>
        
        <h3>Code Example</h3>
        <pre><code>def hello_world():
    print("Hello, Academic World!")
    return True</code></pre>
        
        <blockquote>
            This is a blockquote showing how quoted text appears in this theme.
        </blockquote>
        
        <ul>
            <li>First list item</li>
            <li>Second list item with <code>inline code</code></li>
            <li>Third item with <span class="highlight">highlighted text</span></li>
        </ul>
    </div>
</body>
</html>"""