"""
Tests for the template management system.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from markdown_slides_generator.themes.template_manager import (
    TemplateManager, TemplateConfig, TemplateType, OutputFormat
)
from markdown_slides_generator.utils.exceptions import OutputError


class TestTemplateManager:
    """Test cases for TemplateManager."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_manager = TemplateManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test template manager initialization."""
        assert self.template_manager is not None
        assert self.template_manager.templates_dir.exists()
        
        # Check built-in templates are loaded
        templates = self.template_manager.list_templates()
        assert len(templates) > 0
        assert "academic-slides-revealjs" in templates
        assert "academic-notes-pdf" in templates
    
    def test_get_builtin_template(self):
        """Test getting built-in templates."""
        template = self.template_manager.get_template("academic-slides-revealjs")
        
        assert isinstance(template, TemplateConfig)
        assert template.name == "academic-slides-revealjs"
        assert template.display_name == "Academic Slides (Reveal.js)"
        assert template.template_type == TemplateType.SLIDES
        assert template.output_format == OutputFormat.REVEALJS
        assert len(template.customizable_fields) > 0
        assert "title" in template.required_fields
    
    def test_get_nonexistent_template(self):
        """Test getting non-existent template raises error."""
        with pytest.raises(OutputError, match="Template 'nonexistent' not found"):
            self.template_manager.get_template("nonexistent")
    
    def test_list_templates(self):
        """Test listing all templates."""
        templates = self.template_manager.list_templates()
        
        assert isinstance(templates, dict)
        assert len(templates) >= 4  # At least 4 built-in templates
        
        # Check template info structure
        for template_name, template_info in templates.items():
            assert "display_name" in template_info
            assert "description" in template_info
            assert "template_type" in template_info
            assert "output_format" in template_info
            assert "type" in template_info
            assert "customizable_fields" in template_info
            assert "required_fields" in template_info
    
    def test_render_template_basic(self):
        """Test basic template rendering."""
        content = "# Test Content\n\nThis is test content."
        variables = {
            "title": "Test Presentation",
            "author": "Test Author",
            "date": "2024-01-01"
        }
        
        rendered = self.template_manager.render_template(
            "academic-slides-revealjs",
            content,
            variables
        )
        
        assert isinstance(rendered, str)
        assert len(rendered) > 0
        assert "Test Presentation" in rendered
        assert "Test Author" in rendered
        assert content in rendered
    
    def test_render_template_missing_required_field(self):
        """Test template rendering with missing required field."""
        content = "# Test Content"
        variables = {}  # Missing required 'title' field
        
        with pytest.raises(OutputError, match="Missing required fields"):
            self.template_manager.render_template(
                "academic-slides-revealjs",
                content,
                variables
            )
    
    def test_render_template_with_defaults(self):
        """Test template rendering uses default values."""
        content = "# Test Content"
        variables = {"title": "Test Title"}
        
        rendered = self.template_manager.render_template(
            "academic-slides-revealjs",
            content,
            variables
        )
        
        # Should include default theme
        assert "academic-minimal" in rendered
        # Should include default transition
        assert "slide" in rendered
    
    def test_create_custom_template(self):
        """Test creating custom template."""
        custom_template = self.template_manager.create_custom_template(
            "test-custom-slides",
            TemplateType.SLIDES,
            OutputFormat.REVEALJS,
            base_template="academic-slides-revealjs",
            customizations={
                "description": "Custom test template",
                "default_values": {"theme": "custom-theme"}
            }
        )
        
        assert custom_template.name == "test-custom-slides"
        assert custom_template.template_type == TemplateType.SLIDES
        assert custom_template.output_format == OutputFormat.REVEALJS
        assert custom_template.description == "Custom test template"
        assert custom_template.default_values["theme"] == "custom-theme"
        
        # Verify it's in the list
        templates = self.template_manager.list_templates()
        assert "test-custom-slides" in templates
        assert templates["test-custom-slides"]["type"] == "custom"
    
    def test_create_template_from_scratch(self):
        """Test creating template from scratch."""
        custom_template = self.template_manager.create_custom_template(
            "scratch-template",
            TemplateType.NOTES,
            OutputFormat.PDF,
            customizations={
                "main_template": "# {{ title }}\n\n{{ content }}",
                "yaml_frontmatter": "title: \"{{ title }}\"\nformat: pdf",
                "customizable_fields": ["title", "author"],
                "required_fields": ["title"]
            }
        )
        
        assert custom_template.name == "scratch-template"
        assert custom_template.main_template == "# {{ title }}\n\n{{ content }}"
        assert "title" in custom_template.customizable_fields
        assert "author" in custom_template.customizable_fields
    
    def test_template_suggestions(self):
        """Test getting template suggestions."""
        # Get all slides templates
        slides_templates = self.template_manager.get_template_suggestions(
            template_type=TemplateType.SLIDES
        )
        
        assert len(slides_templates) > 0
        assert "academic-slides-revealjs" in slides_templates
        assert "academic-slides-beamer" in slides_templates
        
        # Get all PDF templates
        pdf_templates = self.template_manager.get_template_suggestions(
            output_format=OutputFormat.PDF
        )
        
        assert len(pdf_templates) > 0
        assert "academic-notes-pdf" in pdf_templates
        assert "academic-handouts-pdf" in pdf_templates
        
        # Get specific combination
        revealjs_slides = self.template_manager.get_template_suggestions(
            template_type=TemplateType.SLIDES,
            output_format=OutputFormat.REVEALJS
        )
        
        assert "academic-slides-revealjs" in revealjs_slides
        # Should not include beamer slides
        assert "academic-slides-beamer" not in revealjs_slides
    
    def test_validate_template(self):
        """Test template validation."""
        validation = self.template_manager.validate_template("academic-slides-revealjs")
        
        assert isinstance(validation, dict)
        assert "valid" in validation
        assert "errors" in validation
        assert "warnings" in validation
        assert "suggestions" in validation
        
        # Built-in template should be valid
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0
    
    def test_validate_invalid_template(self):
        """Test validation of invalid template."""
        # Create template with invalid syntax
        invalid_template = self.template_manager.create_custom_template(
            "invalid-template",
            TemplateType.SLIDES,
            OutputFormat.REVEALJS,
            customizations={
                "main_template": "{{ invalid syntax }",  # Missing closing brace
                "yaml_frontmatter": "title: {{ title }"  # Missing quotes
            }
        )
        
        validation = self.template_manager.validate_template("invalid-template")
        
        assert validation["valid"] is False
        assert len(validation["errors"]) > 0
    
    def test_export_template(self):
        """Test exporting template."""
        export_dir = Path(self.temp_dir) / "exports"
        
        exported_path = self.template_manager.export_template(
            "academic-slides-revealjs",
            str(export_dir)
        )
        
        exported_dir = Path(exported_path)
        assert exported_dir.exists()
        assert exported_dir.is_dir()
        
        # Check exported files
        assert (exported_dir / "template.qmd").exists()
        assert (exported_dir / "frontmatter.yaml").exists()
        assert (exported_dir / "config.json").exists()
        assert (exported_dir / "README.md").exists()
        
        # Check README content
        readme_content = (exported_dir / "README.md").read_text()
        assert "Academic Slides (Reveal.js)" in readme_content
        assert "Customizable Fields" in readme_content
        assert "Required Fields" in readme_content
    
    def test_field_type_validation(self):
        """Test field type validation."""
        template = self.template_manager.get_template("academic-slides-revealjs")
        
        # Valid types
        valid_vars = {
            "title": "Test Title",  # string
            "slide_number": True,   # boolean
            "progress": False       # boolean
        }
        
        # Should not raise error
        self.template_manager._validate_template_variables(template, valid_vars)
        
        # Invalid types
        invalid_vars = {
            "title": "Test Title",
            "slide_number": "not_boolean"  # Should be boolean
        }
        
        with pytest.raises(OutputError, match="Invalid type for field"):
            self.template_manager._validate_template_variables(template, invalid_vars)
    
    def test_template_inheritance(self):
        """Test template inheritance."""
        # Create child template
        child_template = self.template_manager.create_custom_template(
            "child-template",
            TemplateType.SLIDES,
            OutputFormat.REVEALJS,
            base_template="academic-slides-revealjs",
            customizations={
                "description": "Child template",
                "default_values": {"theme": "child-theme"}
            }
        )
        
        assert child_template.parent_template == "academic-slides-revealjs"
        assert child_template.template_type == TemplateType.SLIDES
        assert child_template.output_format == OutputFormat.REVEALJS
        
        # Should inherit customizable fields from parent
        parent_template = self.template_manager.get_template("academic-slides-revealjs")
        assert set(child_template.customizable_fields) == set(parent_template.customizable_fields)
    
    def test_custom_template_persistence(self):
        """Test that custom templates are saved and loaded."""
        # Create custom template
        custom_template = self.template_manager.create_custom_template(
            "persistent-template",
            TemplateType.NOTES,
            OutputFormat.PDF,
            customizations={"description": "Persistent test template"}
        )
        
        # Create new template manager instance (simulates restart)
        new_manager = TemplateManager(self.temp_dir)
        
        # Check if custom template is loaded
        templates = new_manager.list_templates()
        assert "persistent-template" in templates
        
        # Get the template and verify customization
        loaded_template = new_manager.get_template("persistent-template")
        assert loaded_template.description == "Persistent test template"


class TestTemplateRendering:
    """Test cases for template rendering."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_manager = TemplateManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_slides_template_rendering(self):
        """Test rendering slides template."""
        content = """# Introduction

This is the introduction slide.

## Main Content

- Point 1
- Point 2
- Point 3

## Conclusion

Thank you for your attention."""
        
        variables = {
            "title": "My Presentation",
            "author": "John Doe",
            "date": "2024-01-15",
            "theme": "academic-modern"
        }
        
        rendered = self.template_manager.render_template(
            "academic-slides-revealjs",
            content,
            variables
        )
        
        # Check YAML frontmatter
        assert "title: \"My Presentation\"" in rendered
        assert "author: \"John Doe\"" in rendered
        assert "date: \"2024-01-15\"" in rendered
        assert "theme: academic-modern" in rendered
        
        # Check content is included
        assert "# Introduction" in rendered
        assert "## Main Content" in rendered
        assert "- Point 1" in rendered
    
    def test_notes_template_rendering(self):
        """Test rendering notes template."""
        content = """# Chapter 1: Introduction

This chapter covers the basic concepts.

## Section 1.1: Overview

Detailed explanation of the overview.

## Section 1.2: Key Concepts

- Concept A
- Concept B
- Concept C"""
        
        variables = {
            "title": "Course Notes",
            "author": "Professor Smith",
            "course": "CS 101",
            "toc": True,
            "number_sections": True
        }
        
        rendered = self.template_manager.render_template(
            "academic-notes-pdf",
            content,
            variables,
            include_title_slide=False
        )
        
        # Check YAML frontmatter
        assert "title: \"Course Notes\"" in rendered
        assert "author: \"Professor Smith\"" in rendered
        assert "toc: True" in rendered
        assert "number-sections: True" in rendered
        
        # Check content is included
        assert "# Chapter 1: Introduction" in rendered
        assert "## Section 1.1: Overview" in rendered
    
    def test_handouts_template_rendering(self):
        """Test rendering handouts template."""
        content = """# Quick Reference

## Important Formulas

- Formula 1: E = mc²
- Formula 2: F = ma

## Key Points

- Remember this
- Don't forget that"""
        
        variables = {
            "title": "Physics Handout",
            "author": "Dr. Johnson",
            "columns": 2,
            "fontsize": "10pt"
        }
        
        rendered = self.template_manager.render_template(
            "academic-handouts-pdf",
            content,
            variables
        )
        
        # Check YAML frontmatter
        assert "title: \"Physics Handout - Handouts\"" in rendered
        assert "columns: 2" in rendered
        assert "fontsize: 10pt" in rendered
        
        # Check content is included
        assert "# Quick Reference" in rendered
        assert "E = mc²" in rendered
    
    def test_beamer_template_rendering(self):
        """Test rendering Beamer template."""
        content = """# Title Slide

## Slide 1

Content for slide 1.

## Slide 2

Content for slide 2."""
        
        variables = {
            "title": "Beamer Presentation",
            "author": "Speaker Name",
            "institute": "University Name",
            "theme": "Madrid",
            "aspectratio": "169"
        }
        
        rendered = self.template_manager.render_template(
            "academic-slides-beamer",
            content,
            variables
        )
        
        # Check YAML frontmatter
        assert "title: \"Beamer Presentation\"" in rendered
        assert "institute: \"University Name\"" in rendered
        assert "theme: Madrid" in rendered
        assert "aspectratio: 169" in rendered
        
        # Check content is included
        assert "## Slide 1" in rendered
        assert "Content for slide 1" in rendered