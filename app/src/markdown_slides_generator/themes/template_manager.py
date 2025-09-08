"""
Comprehensive template management system.

Provides template system for slides, notes, and handouts with inheritance,
customization capabilities, and validation.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import jinja2
from jinja2 import Environment, FileSystemLoader, Template

from ..utils.logger import get_logger
from ..utils.exceptions import handle_exception, OutputError

logger = get_logger(__name__)


class TemplateType(Enum):
    """Types of templates."""
    SLIDES = "slides"
    NOTES = "notes"
    HANDOUTS = "handouts"
    TITLE_SLIDE = "title_slide"
    SECTION_SLIDE = "section_slide"


class OutputFormat(Enum):
    """Output formats for templates."""
    REVEALJS = "revealjs"
    BEAMER = "beamer"
    PPTX = "pptx"
    PDF = "pdf"
    HTML = "html"


@dataclass
class TemplateConfig:
    """Configuration for a template."""
    name: str
    display_name: str
    template_type: TemplateType
    output_format: OutputFormat
    description: str
    
    # Template inheritance
    parent_template: Optional[str] = None
    
    # Template files
    main_template: str = ""
    css_template: Optional[str] = None
    yaml_frontmatter: Optional[str] = None
    
    # Customization options
    customizable_fields: List[str] = None
    default_values: Dict[str, Any] = None
    
    # Validation rules
    required_fields: List[str] = None
    field_types: Dict[str, str] = None
    
    # Metadata
    author: Optional[str] = None
    version: str = "1.0.0"
    created_date: Optional[str] = None
    modified_date: Optional[str] = None
    
    def __post_init__(self):
        if self.customizable_fields is None:
            self.customizable_fields = []
        if self.default_values is None:
            self.default_values = {}
        if self.required_fields is None:
            self.required_fields = []
        if self.field_types is None:
            self.field_types = {}


class TemplateManager:
    """
    Comprehensive template management system.
    
    Manages templates for slides, notes, and handouts with support for
    inheritance, customization, and validation.
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize template manager.
        
        Args:
            templates_dir: Optional custom templates directory
        """
        self.templates_dir = Path(templates_dir) if templates_dir else self._get_default_templates_dir()
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Template storage
        self._builtin_templates: Dict[str, TemplateConfig] = {}
        self._custom_templates: Dict[str, TemplateConfig] = {}
        
        # Initialize built-in templates
        self._create_builtin_templates()
        self._load_custom_templates()
        
        logger.info(f"Template manager initialized with {len(self._builtin_templates)} built-in templates")
    
    def _get_default_templates_dir(self) -> Path:
        """Get default templates directory."""
        return Path(__file__).parent / "assets" / "templates"
    
    def _create_builtin_templates(self):
        """Create built-in templates."""
        # Create template directories
        for template_type in TemplateType:
            type_dir = self.templates_dir / template_type.value
            type_dir.mkdir(exist_ok=True)
        
        # Academic Slides Template (Reveal.js)
        self._builtin_templates["academic-slides-revealjs"] = TemplateConfig(
            name="academic-slides-revealjs",
            display_name="Academic Slides (Reveal.js)",
            template_type=TemplateType.SLIDES,
            output_format=OutputFormat.REVEALJS,
            description="Professional academic slides template for Reveal.js",
            main_template=self._create_revealjs_slides_template(),
            yaml_frontmatter=self._create_revealjs_yaml_template(),
            customizable_fields=[
                "title", "author", "date", "institute", "theme", 
                "transition", "slide_number", "progress", "controls"
            ],
            default_values={
                "theme": "academic-minimal",
                "transition": "slide",
                "slide_number": True,
                "progress": True,
                "controls": True,
                "center": False,
                "hash": True
            },
            required_fields=["title"],
            field_types={
                "title": "string",
                "author": "string",
                "date": "string",
                "institute": "string",
                "theme": "string",
                "slide_number": "boolean",
                "progress": "boolean",
                "controls": "boolean"
            }
        )
        
        # Academic Notes Template (PDF)
        self._builtin_templates["academic-notes-pdf"] = TemplateConfig(
            name="academic-notes-pdf",
            display_name="Academic Notes (PDF)",
            template_type=TemplateType.NOTES,
            output_format=OutputFormat.PDF,
            description="Comprehensive academic notes template for PDF output",
            main_template=self._create_pdf_notes_template(),
            yaml_frontmatter=self._create_pdf_yaml_template(),
            customizable_fields=[
                "title", "author", "date", "course", "institution",
                "toc", "number_sections", "geometry", "fontsize"
            ],
            default_values={
                "toc": True,
                "number_sections": True,
                "geometry": "margin=1in",
                "fontsize": "11pt",
                "documentclass": "article",
                "linestretch": 1.2
            },
            required_fields=["title"],
            field_types={
                "title": "string",
                "author": "string",
                "date": "string",
                "toc": "boolean",
                "number_sections": "boolean"
            }
        )
        
        # Handouts Template
        self._builtin_templates["academic-handouts-pdf"] = TemplateConfig(
            name="academic-handouts-pdf",
            display_name="Academic Handouts (PDF)",
            template_type=TemplateType.HANDOUTS,
            output_format=OutputFormat.PDF,
            description="Print-friendly handouts template",
            main_template=self._create_handouts_template(),
            yaml_frontmatter=self._create_handouts_yaml_template(),
            customizable_fields=[
                "title", "author", "date", "course", "columns",
                "fontsize", "geometry", "header", "footer"
            ],
            default_values={
                "columns": 2,
                "fontsize": "10pt",
                "geometry": "margin=0.5in",
                "documentclass": "article"
            }
        )
        
        # Beamer Slides Template
        self._builtin_templates["academic-slides-beamer"] = TemplateConfig(
            name="academic-slides-beamer",
            display_name="Academic Slides (Beamer)",
            template_type=TemplateType.SLIDES,
            output_format=OutputFormat.BEAMER,
            description="LaTeX Beamer slides template for academic presentations",
            main_template=self._create_beamer_slides_template(),
            yaml_frontmatter=self._create_beamer_yaml_template(),
            customizable_fields=[
                "title", "author", "date", "institute", "theme",
                "colortheme", "fonttheme", "aspectratio"
            ],
            default_values={
                "theme": "Madrid",
                "colortheme": "default",
                "fonttheme": "default",
                "aspectratio": "169"
            }
        )
        
        # Save built-in templates to disk
        self._save_builtin_templates()
    
    def _create_revealjs_slides_template(self) -> str:
        """Create Reveal.js slides template."""
        return """---
{{ yaml_frontmatter }}
---

{% if title_slide %}
# {{ title }}

{% if author %}**{{ author }}**{% endif %}
{% if institute %}*{{ institute }}*{% endif %}
{% if date %}{{ date }}{% endif %}

---
{% endif %}

{{ content }}"""
    
    def _create_revealjs_yaml_template(self) -> str:
        """Create Reveal.js YAML frontmatter template."""
        return """title: "{{ title }}"
{% if author %}author: "{{ author }}"{% endif %}
{% if date %}date: "{{ date }}"{% endif %}
{% if institute %}institute: "{{ institute }}"{% endif %}
format:
  revealjs:
    theme: {{ theme }}
    transition: {{ transition }}
    slide-number: {{ slide_number }}
    show-slide-number: all
    hash: {{ hash }}
    history: false
    controls: {{ controls }}
    progress: {{ progress }}
    center: {{ center }}
    touch: true
    loop: false
    rtl: false
    navigation-mode: default
    keyboard: true
    overview: true
    help: true
    show-notes: false
    auto-animate: true
    chalkboard:
      theme: whiteboard
      boardmarker-width: 3
      chalkboard-width: 7
      buttons: false
    menu:
      side: left
      width: normal
      numbers: false
      markers: true
      custom: false
      themes: false
      transitions: false
      openButton: true
      keyboard: true
      sticky: false
      autoOpen: false"""
    
    def _create_pdf_notes_template(self) -> str:
        """Create PDF notes template."""
        return """---
{{ yaml_frontmatter }}
---

{% if abstract %}
## Abstract

{{ abstract }}
{% endif %}

{{ content }}

{% if references %}
## References

{{ references }}
{% endif %}"""
    
    def _create_pdf_yaml_template(self) -> str:
        """Create PDF YAML frontmatter template."""
        return """title: "{{ title }}"
{% if author %}author: "{{ author }}"{% endif %}
{% if date %}date: "{{ date }}"{% endif %}
{% if course %}subtitle: "{{ course }}"{% endif %}
format:
  pdf:
    documentclass: {{ documentclass }}
    geometry: {{ geometry }}
    fontsize: {{ fontsize }}
    linestretch: {{ linestretch }}
    toc: {{ toc }}
    toc-depth: 3
    number-sections: {{ number_sections }}
    colorlinks: true
    cite-method: biblatex
    keep-tex: false
    pdf-engine: xelatex
    include-in-header:
      - text: |
          \\usepackage{fancyhdr}
          \\pagestyle{fancy}
          \\fancyhf{}
          \\fancyhead[L]{{ '{' }}{{ title }}{{ '}' }}
          \\fancyhead[R]{\\thepage}
          \\renewcommand{\\headrulewidth}{0.4pt}"""
    
    def _create_handouts_template(self) -> str:
        """Create handouts template."""
        return """---
{{ yaml_frontmatter }}
---

{{ content }}"""
    
    def _create_handouts_yaml_template(self) -> str:
        """Create handouts YAML frontmatter template."""
        return """title: "{{ title }} - Handouts"
{% if author %}author: "{{ author }}"{% endif %}
{% if date %}date: "{{ date }}"{% endif %}
format:
  pdf:
    documentclass: {{ documentclass }}
    geometry: {{ geometry }}
    fontsize: {{ fontsize }}
    columns: {{ columns }}
    toc: false
    number-sections: false
    colorlinks: true
    pdf-engine: xelatex
    include-in-header:
      - text: |
          \\usepackage{multicol}
          \\usepackage{fancyhdr}
          \\pagestyle{fancy}
          \\fancyhf{}
          \\fancyhead[C]{{ '{' }}{{ title }} - Handouts{{ '}' }}
          \\fancyfoot[C]{\\thepage}
          \\renewcommand{\\headrulewidth}{0.4pt}
          \\renewcommand{\\footrulewidth}{0.4pt}"""
    
    def _create_beamer_slides_template(self) -> str:
        """Create Beamer slides template."""
        return """---
{{ yaml_frontmatter }}
---

{{ content }}"""
    
    def _create_beamer_yaml_template(self) -> str:
        """Create Beamer YAML frontmatter template."""
        return """title: "{{ title }}"
{% if author %}author: "{{ author }}"{% endif %}
{% if date %}date: "{{ date }}"{% endif %}
{% if institute %}institute: "{{ institute }}"{% endif %}
format:
  beamer:
    theme: {{ theme }}
    colortheme: {{ colortheme }}
    fonttheme: {{ fonttheme }}
    aspectratio: {{ aspectratio }}
    navigation: horizontal
    pdf-engine: xelatex
    cite-method: biblatex
    slide-level: 2
    section-titles: true
    incremental: false"""
    
    @handle_exception
    def get_template(self, template_name: str) -> TemplateConfig:
        """
        Get template by name.
        
        Args:
            template_name: Name of the template
            
        Returns:
            TemplateConfig object
            
        Raises:
            OutputError: If template not found
        """
        # Check built-in templates first
        if template_name in self._builtin_templates:
            return self._builtin_templates[template_name]
        
        # Check custom templates
        if template_name in self._custom_templates:
            return self._custom_templates[template_name]
        
        raise OutputError(f"Template '{template_name}' not found")
    
    def list_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available templates.
        
        Returns:
            Dictionary with template information
        """
        templates_info = {}
        
        # Built-in templates
        for name, template in self._builtin_templates.items():
            templates_info[name] = {
                'display_name': template.display_name,
                'description': template.description,
                'template_type': template.template_type.value,
                'output_format': template.output_format.value,
                'type': 'built-in',
                'customizable_fields': template.customizable_fields,
                'required_fields': template.required_fields
            }
        
        # Custom templates
        for name, template in self._custom_templates.items():
            templates_info[name] = {
                'display_name': template.display_name,
                'description': template.description,
                'template_type': template.template_type.value,
                'output_format': template.output_format.value,
                'type': 'custom',
                'customizable_fields': template.customizable_fields,
                'required_fields': template.required_fields
            }
        
        return templates_info
    
    @handle_exception
    def render_template(
        self,
        template_name: str,
        content: str,
        variables: Dict[str, Any],
        include_title_slide: bool = True
    ) -> str:
        """
        Render template with content and variables.
        
        Args:
            template_name: Name of template to use
            content: Main content to insert
            variables: Template variables
            include_title_slide: Whether to include title slide
            
        Returns:
            Rendered template string
            
        Raises:
            OutputError: If rendering fails
        """
        logger.debug(f"Rendering template '{template_name}'")
        
        template_config = self.get_template(template_name)
        
        # Validate required fields
        self._validate_template_variables(template_config, variables)
        
        # Merge with default values
        merged_vars = template_config.default_values.copy()
        merged_vars.update(variables)
        merged_vars['content'] = content
        merged_vars['title_slide'] = include_title_slide
        
        try:
            # Render YAML frontmatter
            yaml_template = Template(template_config.yaml_frontmatter)
            yaml_frontmatter = yaml_template.render(**merged_vars)
            
            # Render main template
            main_template = Template(template_config.main_template)
            rendered_content = main_template.render(
                yaml_frontmatter=yaml_frontmatter,
                **merged_vars
            )
            
            logger.debug(f"Successfully rendered template '{template_name}'")
            return rendered_content
            
        except Exception as e:
            raise OutputError(f"Error rendering template '{template_name}': {e}")
    
    def _validate_template_variables(self, template_config: TemplateConfig, variables: Dict[str, Any]):
        """Validate template variables against requirements."""
        # Check required fields
        missing_fields = []
        for field in template_config.required_fields:
            if field not in variables or variables[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            raise OutputError(f"Missing required fields for template '{template_config.name}': {missing_fields}")
        
        # Check field types
        for field, expected_type in template_config.field_types.items():
            if field in variables:
                value = variables[field]
                if not self._validate_field_type(value, expected_type):
                    raise OutputError(f"Invalid type for field '{field}': expected {expected_type}")
    
    def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """Validate field type."""
        type_validators = {
            'string': lambda v: isinstance(v, str),
            'boolean': lambda v: isinstance(v, bool),
            'integer': lambda v: isinstance(v, int),
            'float': lambda v: isinstance(v, (int, float)),
            'list': lambda v: isinstance(v, list),
            'dict': lambda v: isinstance(v, dict)
        }
        
        validator = type_validators.get(expected_type)
        return validator(value) if validator else True
    
    @handle_exception
    def create_custom_template(
        self,
        name: str,
        template_type: TemplateType,
        output_format: OutputFormat,
        base_template: Optional[str] = None,
        customizations: Optional[Dict[str, Any]] = None
    ) -> TemplateConfig:
        """
        Create a custom template.
        
        Args:
            name: Name for the new template
            template_type: Type of template
            output_format: Output format
            base_template: Optional base template to inherit from
            customizations: Optional customizations
            
        Returns:
            New TemplateConfig object
            
        Raises:
            OutputError: If creation fails
        """
        logger.info(f"Creating custom template '{name}'")
        
        # Get base template if specified
        if base_template:
            base = self.get_template(base_template)
            template_dict = asdict(base)
            template_dict['name'] = name
            template_dict['display_name'] = name.replace('-', ' ').title()
            template_dict['parent_template'] = base_template
        else:
            # Create from scratch
            template_dict = {
                'name': name,
                'display_name': name.replace('-', ' ').title(),
                'template_type': template_type,
                'output_format': output_format,
                'description': f"Custom {template_type.value} template",
                'main_template': "{{ content }}",
                'yaml_frontmatter': "title: \"{{ title }}\"",
                'customizable_fields': ['title'],
                'default_values': {},
                'required_fields': ['title'],
                'field_types': {'title': 'string'}
            }
        
        # Apply customizations
        if customizations:
            template_dict.update(customizations)
        
        # Create template object
        custom_template = TemplateConfig(**template_dict)
        
        # Save custom template
        self._save_custom_template(custom_template)
        self._custom_templates[name] = custom_template
        
        logger.info(f"Created custom template '{name}'")
        return custom_template
    
    def get_template_suggestions(
        self,
        template_type: Optional[TemplateType] = None,
        output_format: Optional[OutputFormat] = None
    ) -> List[str]:
        """
        Get template suggestions based on criteria.
        
        Args:
            template_type: Optional template type filter
            output_format: Optional output format filter
            
        Returns:
            List of matching template names
        """
        suggestions = []
        
        all_templates = {**self._builtin_templates, **self._custom_templates}
        
        for name, template in all_templates.items():
            if template_type and template.template_type != template_type:
                continue
            if output_format and template.output_format != output_format:
                continue
            suggestions.append(name)
        
        return suggestions
    
    def _save_builtin_templates(self):
        """Save built-in templates to disk."""
        for name, template in self._builtin_templates.items():
            template_dir = self.templates_dir / template.template_type.value / name
            template_dir.mkdir(parents=True, exist_ok=True)
            
            # Save main template
            main_file = template_dir / "template.qmd"
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(template.main_template)
            
            # Save YAML template
            if template.yaml_frontmatter:
                yaml_file = template_dir / "frontmatter.yaml"
                with open(yaml_file, 'w', encoding='utf-8') as f:
                    f.write(template.yaml_frontmatter)
            
            # Save config
            config_file = template_dir / "config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(template), f, indent=2, default=str)
    
    def _load_custom_templates(self):
        """Load custom templates from disk."""
        custom_templates_file = self.templates_dir / "custom_templates.json"
        
        if not custom_templates_file.exists():
            return
        
        try:
            with open(custom_templates_file, 'r', encoding='utf-8') as f:
                templates_data = json.load(f)
            
            for template_data in templates_data:
                # Convert enum strings back to enums
                if 'template_type' in template_data and isinstance(template_data['template_type'], str):
                    template_data['template_type'] = TemplateType(template_data['template_type'])
                if 'output_format' in template_data and isinstance(template_data['output_format'], str):
                    template_data['output_format'] = OutputFormat(template_data['output_format'])
                
                template = TemplateConfig(**template_data)
                self._custom_templates[template.name] = template
            
            logger.info(f"Loaded {len(self._custom_templates)} custom templates")
            
        except Exception as e:
            logger.error(f"Error loading custom templates: {e}")
    
    def _save_custom_template(self, template: TemplateConfig):
        """Save custom template to disk."""
        custom_templates_file = self.templates_dir / "custom_templates.json"
        
        try:
            # Load existing templates
            templates_data = []
            if custom_templates_file.exists():
                with open(custom_templates_file, 'r', encoding='utf-8') as f:
                    templates_data = json.load(f)
            
            # Add or update template
            template_dict = asdict(template)
            
            # Convert enums to their values for JSON serialization
            if 'template_type' in template_dict and hasattr(template_dict['template_type'], 'value'):
                template_dict['template_type'] = template_dict['template_type'].value
            if 'output_format' in template_dict and hasattr(template_dict['output_format'], 'value'):
                template_dict['output_format'] = template_dict['output_format'].value
            
            templates_data = [t for t in templates_data if t['name'] != template.name]
            templates_data.append(template_dict)
            
            # Save back to file
            with open(custom_templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates_data, f, indent=2, default=str)
            
            logger.debug(f"Saved custom template '{template.name}'")
            
        except Exception as e:
            logger.error(f"Error saving custom template: {e}")
    
    @handle_exception
    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """
        Validate a template configuration.
        
        Args:
            template_name: Name of template to validate
            
        Returns:
            Validation results dictionary
            
        Raises:
            OutputError: If template not found
        """
        template = self.get_template(template_name)
        
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Check template syntax
        try:
            Template(template.main_template)
        except Exception as e:
            validation_results['valid'] = False
            validation_results['errors'].append(f"Invalid main template syntax: {e}")
        
        # Check YAML frontmatter syntax
        if template.yaml_frontmatter:
            try:
                Template(template.yaml_frontmatter)
            except Exception as e:
                validation_results['valid'] = False
                validation_results['errors'].append(f"Invalid YAML frontmatter syntax: {e}")
        
        # Check required fields
        if not template.required_fields:
            validation_results['warnings'].append("No required fields defined")
        
        # Check customizable fields
        if not template.customizable_fields:
            validation_results['warnings'].append("No customizable fields defined")
        
        return validation_results
    
    def export_template(self, template_name: str, output_dir: str) -> str:
        """
        Export template to directory.
        
        Args:
            template_name: Name of template to export
            output_dir: Directory to export to
            
        Returns:
            Path to exported template directory
        """
        template = self.get_template(template_name)
        export_path = Path(output_dir) / template_name
        export_path.mkdir(parents=True, exist_ok=True)
        
        # Export main template
        main_file = export_path / "template.qmd"
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(template.main_template)
        
        # Export YAML frontmatter
        if template.yaml_frontmatter:
            yaml_file = export_path / "frontmatter.yaml"
            with open(yaml_file, 'w', encoding='utf-8') as f:
                f.write(template.yaml_frontmatter)
        
        # Export configuration
        config_file = export_path / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(template), f, indent=2, default=str)
        
        # Export README
        readme_file = export_path / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(self._generate_template_readme(template))
        
        logger.info(f"Exported template '{template_name}' to {export_path}")
        return str(export_path)
    
    def _generate_template_readme(self, template: TemplateConfig) -> str:
        """Generate README for exported template."""
        return f"""# {template.display_name}

{template.description}

## Template Information

- **Type**: {template.template_type.value}
- **Output Format**: {template.output_format.value}
- **Version**: {template.version}

## Customizable Fields

{chr(10).join(f"- `{field}`" for field in template.customizable_fields)}

## Required Fields

{chr(10).join(f"- `{field}`" for field in template.required_fields)}

## Default Values

```yaml
{yaml.dump(template.default_values, default_flow_style=False)}
```

## Usage

Use this template with the markdown slides generator:

```bash
markdown-slides-generator input.md --template {template.name}
```
"""