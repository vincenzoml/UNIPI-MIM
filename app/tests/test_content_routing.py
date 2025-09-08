"""
Tests for the intelligent content routing system.

Tests the generation of clean Quarto .qmd files with proper YAML frontmatter
and intelligent slide boundary detection.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import yaml

from markdown_slides_generator.core.content_splitter import ContentSplitter


class TestIntelligentContentRouting:
    """Test the intelligent content routing and Quarto file generation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.splitter = ContentSplitter()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_quarto_file_generation(self):
        """Test generation of Quarto .qmd files."""
        # Create test markdown file
        test_content = """# Test Lecture

Introduction content.

## Section 1

Content for section 1.

<!-- SLIDE-ONLY -->
Slide-only content.

<!-- NOTES-ONLY -->
Notes-only content.

<!-- ALL -->
## Section 2

Final content."""
        
        test_file = self.temp_path / "test.md"
        test_file.write_text(test_content)
        
        # Generate Quarto files
        slides_path, notes_path = self.splitter.generate_quarto_files(
            str(test_file), 
            str(self.temp_path / "output")
        )
        
        # Check files were created
        assert Path(slides_path).exists()
        assert Path(notes_path).exists()
        
        # Check file names
        assert "test_slides.qmd" in slides_path
        assert "test_notes.qmd" in notes_path
    
    def test_slides_yaml_frontmatter(self):
        """Test that slides have proper YAML frontmatter."""
        test_content = """# Sample Lecture

Content here."""
        
        test_file = self.temp_path / "sample.md"
        test_file.write_text(test_content)
        
        slides_path, _ = self.splitter.generate_quarto_files(
            str(test_file), 
            str(self.temp_path / "output")
        )
        
        # Read generated slides file
        slides_content = Path(slides_path).read_text()
        
        # Check YAML frontmatter
        assert slides_content.startswith("---\n")
        
        # Extract YAML
        yaml_end = slides_content.find("---\n", 4)
        yaml_content = slides_content[4:yaml_end]
        config = yaml.safe_load(yaml_content)
        
        # Verify YAML structure
        assert "title" in config
        assert "format" in config
        assert "revealjs" in config["format"]
        assert config["format"]["revealjs"]["theme"] == "white"
        assert config["format"]["revealjs"]["slide-number"] is True
    
    def test_notes_yaml_frontmatter(self):
        """Test that notes have proper academic YAML frontmatter."""
        test_content = """# Academic Lecture

Detailed content."""
        
        test_file = self.temp_path / "academic.md"
        test_file.write_text(test_content)
        
        _, notes_path = self.splitter.generate_quarto_files(
            str(test_file), 
            str(self.temp_path / "output")
        )
        
        # Read generated notes file
        notes_content = Path(notes_path).read_text()
        
        # Extract YAML
        yaml_end = notes_content.find("---\n", 4)
        yaml_content = notes_content[4:yaml_end]
        config = yaml.safe_load(yaml_content)
        
        # Verify academic formatting
        assert "Lecture Notes" in config["title"]
        assert "pdf" in config["format"]
        assert "html" in config["format"]
        assert config["format"]["pdf"]["toc"] is True
        assert config["format"]["pdf"]["number-sections"] is True
    
    def test_intelligent_slide_splitting(self):
        """Test intelligent slide boundary detection."""
        test_content = """# Main Title

Introduction paragraph.

## Section A

Content for section A with some details.

### Subsection A1

More detailed content here.

## Section B

Different content for section B."""
        
        # Process content to get slide sections
        processed = self.splitter.process_directives(test_content)
        slide_sections = self.splitter._create_intelligent_slides(processed["slides"])
        
        # Should create multiple slide sections based on headers
        assert len(slide_sections) >= 3  # Main, Section A, Section B
        
        # Check titles
        titles = [section.title for section in slide_sections]
        assert any("Section A" in title for title in titles)
        assert any("Section B" in title for title in titles)
    
    def test_long_slide_splitting(self):
        """Test automatic splitting of overly long slides."""
        # Create content that exceeds word limit
        long_content = """# Long Section

""" + " ".join(["Word"] * 200)  # 200 words, exceeds typical limit
        
        slide_sections = self.splitter._create_intelligent_slides(long_content)
        
        # Should split into multiple sections
        assert len(slide_sections) > 1
        
        # Check that split sections have reasonable word counts
        for section in slide_sections:
            assert section.word_count <= 150  # Within reasonable limit
    
    def test_content_analysis(self):
        """Test analysis of content characteristics."""
        test_content = """# Code Example

Here's some Python code:

```python
def hello():
    print("Hello, World!")
```

And here's a math formula: $E = mc^2$

Regular text content."""
        
        slide_sections = self.splitter._create_intelligent_slides(test_content)
        
        # Should detect code and math
        section = slide_sections[0]
        assert section.has_code is True
        assert section.has_math is True
    
    def test_slide_separator_insertion(self):
        """Test that slide separators are properly inserted."""
        test_content = """# Title 1

Content 1.

# Title 2

Content 2."""
        
        slide_sections = self.splitter._create_intelligent_slides(test_content)
        formatted = self.splitter._format_slides_content(slide_sections)
        
        # Should contain slide separators
        assert "---" in formatted
        
        # Should have proper structure
        assert "# Title 1" in formatted
        assert "# Title 2" in formatted
    
    def test_speaker_notes_generation(self):
        """Test generation of speaker notes for complex slides."""
        test_content = """# Complex Slide

```python
# This is code
print("test")
```

Mathematical formula: $x = y + z$

Lots of content here to make it complex."""
        
        slide_sections = self.splitter._create_intelligent_slides(test_content)
        formatted = self.splitter._format_slides_content(slide_sections)
        
        # Should contain speaker notes
        assert "::: {.notes}" in formatted
        assert ":::" in formatted
        assert "code examples" in formatted.lower()
        assert "mathematical expressions" in formatted.lower()
    
    def test_preserve_markdown_structure(self):
        """Test that markdown structure is preserved in output."""
        test_content = """# Main Title

## Subsection

- List item 1
- List item 2

1. Numbered item
2. Another item

> This is a blockquote

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |

**Bold text** and *italic text*."""
        
        processed = self.splitter.process_directives(test_content)
        
        # Check that structure is preserved in both outputs
        slides = processed["slides"]
        notes = processed["notes"]
        
        # Both should contain the same structural elements
        for content in [slides, notes]:
            assert "- List item 1" in content
            assert "1. Numbered item" in content
            assert "> This is a blockquote" in content
            assert "| Column 1 |" in content
            assert "**Bold text**" in content
    
    def test_empty_content_handling(self):
        """Test handling of empty or minimal content."""
        test_content = """# Just a Title

"""
        
        test_file = self.temp_path / "minimal.md"
        test_file.write_text(test_content)
        
        # Should not crash with minimal content
        slides_path, notes_path = self.splitter.generate_quarto_files(
            str(test_file), 
            str(self.temp_path / "output")
        )
        
        # Files should still be created
        assert Path(slides_path).exists()
        assert Path(notes_path).exists()
        
        # Should have valid YAML and content
        slides_content = Path(slides_path).read_text()
        assert "title:" in slides_content
        assert "# Just a Title" in slides_content


if __name__ == "__main__":
    pytest.main([__file__])