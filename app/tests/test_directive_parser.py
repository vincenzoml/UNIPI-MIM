"""
Comprehensive tests for the markdown directive parser.

Tests the robust parsing of special markdown comments and state machine
implementation for content mode tracking with extensive edge cases.
"""

import pytest
from markdown_slides_generator.core.content_splitter import (
    MarkdownDirectiveParser, 
    ContentSplitter,
    ContentMode,
    DirectiveMatch,
    ContentBlock
)


class TestMarkdownDirectiveParser:
    """Test the markdown directive parser functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = MarkdownDirectiveParser()
    
    def test_parse_basic_directives(self):
        """Test parsing of basic directive types."""
        content = """
# Introduction
Some content here.

<!-- SLIDE -->
This is slide content.

<!-- SLIDE-ONLY -->
Only in slides.

<!-- NOTES-ONLY -->
Only in notes.

<!-- ALL -->
Back to normal.
"""
        directives = self.parser.parse_directives(content)
        
        assert len(directives) == 4
        assert directives[0].mode == ContentMode.SLIDE_BOUNDARY
        assert directives[1].mode == ContentMode.SLIDES_ONLY
        assert directives[2].mode == ContentMode.NOTES_ONLY
        assert directives[3].mode == ContentMode.ALL
    
    def test_case_insensitive_directives(self):
        """Test that directives are case insensitive."""
        content = """
<!-- slide -->
<!-- SLIDE-only -->
<!-- notes-ONLY -->
<!-- all -->
"""
        directives = self.parser.parse_directives(content)
        
        assert len(directives) == 4
        assert directives[0].mode == ContentMode.SLIDE_BOUNDARY
        assert directives[1].mode == ContentMode.SLIDES_ONLY
        assert directives[2].mode == ContentMode.NOTES_ONLY
        assert directives[3].mode == ContentMode.ALL
    
    def test_whitespace_flexibility(self):
        """Test that directives handle flexible whitespace."""
        content = """
<!--SLIDE-->
<!--  SLIDE-ONLY  -->
<!-- NOTES-ONLY-->
<!--ALL -->
"""
        directives = self.parser.parse_directives(content)
        
        assert len(directives) == 4
        for directive in directives:
            assert directive.mode in [ContentMode.SLIDE_BOUNDARY, ContentMode.SLIDES_ONLY, 
                                    ContentMode.NOTES_ONLY, ContentMode.ALL]
    
    def test_line_number_tracking(self):
        """Test that line numbers are correctly tracked."""
        content = """Line 1
Line 2
<!-- SLIDE -->
Line 4
<!-- NOTES-ONLY -->
Line 6"""
        
        directives = self.parser.parse_directives(content)
        
        assert len(directives) == 2
        assert directives[0].line_number == 3
        assert directives[1].line_number == 5
    
    def test_multiple_directives_per_line(self):
        """Test handling multiple directives on the same line."""
        content = "<!-- SLIDE --> Some content <!-- NOTES-ONLY -->"
        
        directives = self.parser.parse_directives(content)
        
        assert len(directives) == 2
        assert directives[0].mode == ContentMode.SLIDE_BOUNDARY
        assert directives[1].mode == ContentMode.NOTES_ONLY
        assert directives[0].position < directives[1].position
    
    def test_malformed_directive_detection(self):
        """Test detection of malformed directives."""
        content = """
<!-- SLDIE -->
<!-- SLIDE_ONLY -->
<!-- NOTE-ONLY -->
<!-- SLIDE -->
"""
        
        self.parser.parse_directives(content)
        
        # Should detect malformed directives (NOTE-ONLY should be NOTES-ONLY)
        assert len(self.parser.malformed_directives) > 0
        
        # Check that NOTE-ONLY was detected as malformed
        malformed_texts = [m['text'] for m in self.parser.malformed_directives]
        assert any('NOTE-ONLY' in text for text in malformed_texts)
    
    def test_content_block_processing(self):
        """Test processing content into blocks with correct modes."""
        content = """# Introduction
This is intro content.

<!-- SLIDE-ONLY -->
Slide only content.

<!-- NOTES-ONLY -->
Notes only content.

<!-- ALL -->
Normal content again."""
        
        directives = self.parser.parse_directives(content)
        blocks = self.parser.process_content_blocks(content, directives)
        
        assert len(blocks) == 4
        assert blocks[0].mode == ContentMode.ALL  # Introduction
        assert blocks[1].mode == ContentMode.SLIDES_ONLY
        assert blocks[2].mode == ContentMode.NOTES_ONLY
        assert blocks[3].mode == ContentMode.ALL
    
    def test_empty_content_blocks(self):
        """Test that empty content blocks are filtered out."""
        content = """<!-- SLIDE-ONLY -->

<!-- NOTES-ONLY -->
Some content.
<!-- ALL -->"""
        
        directives = self.parser.parse_directives(content)
        blocks = self.parser.process_content_blocks(content, directives)
        
        # Should only have blocks with actual content
        assert all(block.content.strip() for block in blocks)
    
    def test_directive_validation(self):
        """Test validation of directive structure."""
        content = """
<!-- SLIDE-ONLY -->
Some content.
<!-- NOTES-ONLY -->
More content.
<!-- ALL -->
Normal content.
<!-- ALL -->
"""
        
        directives = self.parser.parse_directives(content)
        warnings = self.parser.validate_directive_structure(directives)
        
        # Should warn about nested mode directive and extra ALL directive
        assert len(warnings) > 0
        assert any("Nested mode directive" in warning or "without matching mode directive" in warning 
                  for warning in warnings)
    
    def test_unclosed_directive_validation(self):
        """Test validation of unclosed directives."""
        content = """
<!-- SLIDE-ONLY -->
Some content.
<!-- NOTES-ONLY -->
More content.
"""
        
        directives = self.parser.parse_directives(content)
        warnings = self.parser.validate_directive_structure(directives)
        
        # Should warn about unclosed directives
        assert len(warnings) > 0
        assert any("Unclosed" in warning for warning in warnings)


class TestContentSplitter:
    """Test the content splitter integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.splitter = ContentSplitter()
    
    def test_basic_content_splitting(self):
        """Test basic content splitting functionality."""
        content = """# Lecture Title

Introduction content for both.

<!-- SLIDE-ONLY -->
This appears only in slides.

<!-- NOTES-ONLY -->
This appears only in notes.

<!-- ALL -->
This appears in both again."""
        
        result = self.splitter.process_directives(content)
        
        assert "slides" in result
        assert "notes" in result
        
        # Check slides content
        slides = result["slides"]
        assert "Introduction content for both" in slides
        assert "This appears only in slides" in slides
        assert "This appears only in notes" not in slides
        assert "This appears in both again" in slides
        
        # Check notes content
        notes = result["notes"]
        assert "Introduction content for both" in notes
        assert "This appears only in slides" not in notes
        assert "This appears only in notes" in notes
        assert "This appears in both again" in notes
    
    def test_slide_boundary_tracking(self):
        """Test that slide boundaries are tracked correctly."""
        content = """# Title

Content 1

<!-- SLIDE -->
Content 2

<!-- SLIDE -->
Content 3"""
        
        self.splitter.process_directives(content)
        boundaries = self.splitter.get_slide_boundaries()
        
        assert len(boundaries) == 2
        assert 5 in boundaries  # Line numbers where SLIDE directives appear
        assert 8 in boundaries
    
    def test_validation_warnings_access(self):
        """Test access to validation warnings."""
        content = """
<!-- SLIDE-ONLY -->
Content
<!-- ALL -->
More content
<!-- ALL -->
"""
        
        self.splitter.process_directives(content)
        warnings = self.splitter.get_validation_warnings()
        
        assert len(warnings) > 0
    
    def test_no_directives_handling(self):
        """Test handling content with no directives."""
        content = """# Simple Lecture

Just normal markdown content.

## Section 1

More content here."""
        
        result = self.splitter.process_directives(content)
        
        # Both slides and notes should have the same content
        assert result["slides"] == result["notes"]
        assert "Simple Lecture" in result["slides"]
        assert "Section 1" in result["notes"]
    
    def test_complex_nested_content(self):
        """Test complex content with nested structures."""
        content = """# Main Title

## Introduction
Normal content here.

<!-- SLIDE-ONLY -->
### Slide-only Section
- Point 1
- Point 2

```python
# Code only in slides
print("hello")
```
<!-- NOTES-ONLY -->

### Notes-only Section
Detailed explanation with:

1. First point
2. Second point

Mathematical formula: $E = mc^2$

<!-- ALL -->
## Conclusion
Final thoughts for both."""
        
        result = self.splitter.process_directives(content)
        
        slides = result["slides"]
        notes = result["notes"]
        
        # Check slides content
        assert "Slide-only Section" in slides
        assert 'print("hello")' in slides
        assert "Notes-only Section" not in slides
        assert "Final thoughts" in slides
        
        # Check notes content
        assert "Slide-only Section" not in notes
        assert 'print("hello")' not in notes
        assert "Notes-only Section" in notes
        assert "$E = mc^2$" in notes
        assert "Final thoughts" in notes


class TestDirectiveParserEdgeCases:
    """Test edge cases and error conditions in directive parsing."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = MarkdownDirectiveParser()
    
    def test_nested_html_comments(self):
        """Test handling of nested HTML comments."""
        content = """
<!-- This is a regular comment -->
<!-- SLIDE -->
<!-- Another comment with <!-- nested --> content -->
<!-- NOTES-ONLY -->
Content here.
"""
        directives = self.parser.parse_directives(content)
        
        # Should find SLIDE and NOTES-ONLY directives
        assert len(directives) == 2
        assert directives[0].mode == ContentMode.SLIDE_BOUNDARY
        assert directives[1].mode == ContentMode.NOTES_ONLY
    
    def test_directive_in_code_blocks(self):
        """Test that directives in code blocks are ignored."""
        content = """
```html
<!-- SLIDE -->
This should not be parsed as a directive
```

<!-- SLIDE-ONLY -->
This should be parsed.
"""
        directives = self.parser.parse_directives(content)
        
        # Should only find the SLIDE-ONLY directive outside code block
        assert len(directives) == 1
        assert directives[0].mode == ContentMode.SLIDES_ONLY
    
    def test_directive_in_inline_code(self):
        """Test that directives in inline code are ignored."""
        content = """
Here's some code: `<!-- SLIDE -->` that should be ignored.

<!-- NOTES-ONLY -->
This should be parsed.
"""
        directives = self.parser.parse_directives(content)
        
        # Should only find the NOTES-ONLY directive
        assert len(directives) == 1
        assert directives[0].mode == ContentMode.NOTES_ONLY
    
    def test_malformed_directive_suggestions(self):
        """Test suggestions for malformed directives."""
        content = """
<!-- SLDIE -->
<!-- SLIDE_ONLY -->
<!-- NOTE-ONLY -->
<!-- SLIDES-ONLY -->
"""
        
        self.parser.parse_directives(content)
        
        # Check malformed directive suggestions
        assert len(self.parser.malformed_directives) >= 2
        
        suggestions = [m['suggestion'] for m in self.parser.malformed_directives]
        assert '<!-- SLIDE -->' in suggestions
        assert '<!-- NOTES-ONLY -->' in suggestions
    
    def test_unicode_in_directives(self):
        """Test handling of unicode characters around directives."""
        content = """
# Título con acentos

<!-- SLIDE -->
## Sección con ñ

<!-- NOTES-ONLY -->
Contenido en español: áéíóú
"""
        
        directives = self.parser.parse_directives(content)
        blocks = self.parser.process_content_blocks(content, directives)
        
        assert len(directives) == 2
        assert len(blocks) == 3
        
        # Check that unicode content is preserved
        spanish_block = next(b for b in blocks if 'español' in b.content)
        assert 'áéíóú' in spanish_block.content
    
    def test_very_long_content_blocks(self):
        """Test handling of very long content blocks."""
        # Create a very long content block
        long_content = "Word " * 10000  # 10,000 words
        content = f"""
<!-- SLIDE-ONLY -->
{long_content}
<!-- ALL -->
Normal content.
"""
        
        directives = self.parser.parse_directives(content)
        blocks = self.parser.process_content_blocks(content, directives)
        
        assert len(blocks) == 2
        assert len(blocks[0].content.split()) >= 10000
    
    def test_empty_directive_blocks(self):
        """Test handling of empty blocks between directives."""
        content = """
<!-- SLIDE-ONLY -->

<!-- NOTES-ONLY -->

<!-- ALL -->
Some content.
"""
        
        directives = self.parser.parse_directives(content)
        blocks = self.parser.process_content_blocks(content, directives)
        
        # Should filter out empty blocks
        assert all(block.content.strip() for block in blocks)
    
    def test_directive_at_file_boundaries(self):
        """Test directives at the very start and end of files."""
        content = """<!-- SLIDE-ONLY -->
Content at start.
<!-- NOTES-ONLY -->
Content in middle.
<!-- ALL -->
Content at end."""
        
        directives = self.parser.parse_directives(content)
        blocks = self.parser.process_content_blocks(content, directives)
        
        assert len(directives) == 3
        assert len(blocks) == 3
        assert blocks[0].mode == ContentMode.SLIDES_ONLY
        assert blocks[1].mode == ContentMode.NOTES_ONLY
        assert blocks[2].mode == ContentMode.ALL


class TestContentSplitterPerformance:
    """Test performance characteristics of content splitter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.splitter = ContentSplitter()
    
    def test_large_file_processing(self):
        """Test processing of large markdown files."""
        import time
        
        # Create a large markdown file (simulate 1MB content)
        sections = []
        for i in range(1000):
            sections.append(f"""
## Section {i}

This is section {i} with some content. Lorem ipsum dolor sit amet, 
consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore 
et dolore magna aliqua.

<!-- SLIDE -->

### Subsection {i}.1

More content here with mathematical expressions: $x = y + z_{i}$

<!-- NOTES-ONLY -->
Detailed explanation for section {i} that only appears in notes.
This includes additional context and background information.

<!-- ALL -->
""")
        
        large_content = '\n'.join(sections)
        
        start_time = time.time()
        result = self.splitter.process_directives(large_content)
        processing_time = time.time() - start_time
        
        # Should process within reasonable time (< 5 seconds for 1MB)
        assert processing_time < 5.0
        
        # Should produce valid results
        assert len(result["slides"]) > 0
        assert len(result["notes"]) > 0
        assert len(result["blocks"]) > 0
    
    def test_many_directives_performance(self):
        """Test performance with many directives."""
        import time
        
        # Create content with many directives
        content_parts = ["# Test Document\n"]
        for i in range(500):  # 500 directive pairs
            content_parts.extend([
                f"Content block {i}\n",
                "<!-- SLIDE-ONLY -->\n",
                f"Slide content {i}\n",
                "<!-- NOTES-ONLY -->\n", 
                f"Notes content {i}\n",
                "<!-- ALL -->\n"
            ])
        
        content = ''.join(content_parts)
        
        start_time = time.time()
        result = self.splitter.process_directives(content)
        processing_time = time.time() - start_time
        
        # Should handle many directives efficiently
        assert processing_time < 2.0
        assert len(result["directives"]) == 1500  # 3 directives per iteration


class TestContentSplitterIntegration:
    """Integration tests for content splitter with other components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.splitter = ContentSplitter()
    
    def test_latex_integration(self):
        """Test integration with LaTeX processor."""
        content = """
# Mathematical Content

## Basic Math
Inline math: $E = mc^2$

Display math:
$$\\int_0^1 x^2 dx = \\frac{1}{3}$$

<!-- SLIDE-ONLY -->
## Advanced Math
Complex equation: $\\sum_{i=1}^n \\frac{1}{i^2} = \\frac{\\pi^2}{6}$

<!-- NOTES-ONLY -->
## Detailed Derivation
The proof involves...
$$\\begin{align}
\\sum_{i=1}^n \\frac{1}{i^2} &= 1 + \\frac{1}{4} + \\frac{1}{9} + \\cdots \\\\
&= \\frac{\\pi^2}{6}
\\end{align}$$
"""
        
        result = self.splitter.process_directives(content)
        
        # Check LaTeX validation was performed
        latex_result = self.splitter.get_latex_validation_result()
        assert latex_result is not None
        
        # Should detect math in both slides and notes
        assert '$E = mc^2$' in result["slides"]
        assert '$E = mc^2$' in result["notes"]
        assert '\\sum_{i=1}^n' in result["slides"]
        assert '\\begin{align}' in result["notes"]
        assert '\\begin{align}' not in result["slides"]
    
    def test_quarto_file_generation_integration(self):
        """Test integration with Quarto file generation."""
        import tempfile
        import shutil
        from pathlib import Path
        
        content = """---
title: "Test Lecture"
author: "Test Author"
---

# Introduction

This is a test lecture.

<!-- SLIDE -->
## Main Content

Key points:
- Point 1
- Point 2

<!-- NOTES-ONLY -->
## Additional Details

Extended explanation that only appears in notes.
"""
        
        # Create temporary directory and file
        temp_dir = tempfile.mkdtemp()
        try:
            temp_file = Path(temp_dir) / "test.md"
            temp_file.write_text(content)
            
            # Generate Quarto files
            slides_path, notes_path = self.splitter.generate_quarto_files(
                str(temp_file), str(Path(temp_dir) / "output")
            )
            
            # Check files were created
            assert Path(slides_path).exists()
            assert Path(notes_path).exists()
            
            # Check content
            slides_content = Path(slides_path).read_text()
            notes_content = Path(notes_path).read_text()
            
            # Should have YAML frontmatter
            assert slides_content.startswith("---\n")
            assert notes_content.startswith("---\n")
            
            # Should have appropriate content
            assert "Key points:" in slides_content
            assert "Extended explanation" in notes_content
            assert "Extended explanation" not in slides_content
            
        finally:
            shutil.rmtree(temp_dir)


class TestNewDirectiveFeatures:
    """Test new directive features: case-insensitive SLIDES and NOTES boundary."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = MarkdownDirectiveParser()
        self.splitter = ContentSplitter()
    
    def test_case_insensitive_slides_directive(self):
        """Test that SLIDES directive works in both upper and lower case."""
        content = """
# Intro
Some content.

<!-- slide -->
Lower case slide.

<!-- SLIDE -->
Upper case slide.

<!-- Slides -->
Mixed case slides.

<!-- SLIDES -->
Plural slides.
"""
        directives = self.parser.parse_directives(content)
        
        # Should find all 4 directives as SLIDE_BOUNDARY
        assert len(directives) == 4
        for directive in directives:
            assert directive.mode == ContentMode.SLIDE_BOUNDARY
        
        # Test specific patterns
        assert any('<!-- slide -->' in d.directive.lower() for d in directives)
        assert any('<!-- slides -->' in d.directive.lower() for d in directives)
    
    def test_notes_directive_as_boundary_and_mode(self):
        """Test that NOTES directive acts as both slide boundary and notes-only mode."""
        content = """
# Introduction
This appears in both.

<!-- NOTES -->
This content should appear only in notes and start a new slide.
More notes content here.

<!-- ALL -->
Back to both slides and notes.
"""
        
        # Test directive parsing
        directives = self.parser.parse_directives(content)
        assert len(directives) == 2
        assert directives[0].mode == ContentMode.NOTES_SLIDE_BOUNDARY
        assert directives[1].mode == ContentMode.ALL
        
        # Test content splitting
        result = self.splitter.process_directives(content)
        slides_content = result["slides"]
        notes_content = result["notes"]
        
        # Slides should NOT contain the notes content
        assert "This content should appear only in notes" not in slides_content
        assert "More notes content here" not in slides_content
        
        # Notes should contain all content
        assert "This appears in both" in notes_content
        assert "This content should appear only in notes" in notes_content
        assert "Back to both slides and notes" in notes_content
        
        # Check slide boundaries are tracked
        assert len(self.splitter.slide_boundaries) == 1
    
    def test_notes_directive_case_variations(self):
        """Test NOTES directive with different case variations."""
        content = """
<!-- notes -->
Lower case notes.

<!-- NOTES -->  
Upper case notes.

<!-- Notes -->
Mixed case notes.
"""
        directives = self.parser.parse_directives(content)
        
        assert len(directives) == 3
        for directive in directives:
            assert directive.mode == ContentMode.NOTES_SLIDE_BOUNDARY
    
    def test_notes_directive_with_state_management(self):
        """Test NOTES directive properly manages state transitions."""
        content = """
Normal content.

<!-- SLIDE-ONLY -->
Slides only content.

<!-- NOTES -->
This should be notes only and end the slides-only section.

<!-- ALL -->
Back to normal.
"""
        
        # Process content blocks
        directives = self.parser.parse_directives(content)
        blocks = self.parser.process_content_blocks(content, directives)
        
        # Check block modes
        assert len(blocks) == 4
        assert blocks[0].mode == ContentMode.ALL  # Normal content
        assert blocks[1].mode == ContentMode.SLIDES_ONLY  # Slides only content  
        assert blocks[2].mode == ContentMode.NOTES_ONLY  # Notes directive content
        assert blocks[3].mode == ContentMode.ALL  # Back to normal
    
    def test_malformed_directive_suggestions_with_notes(self):
        """Test suggestions for malformed NOTES and SLIDES directives."""
        content = """
<!-- SLDIE -->
<!-- NOTE -->
<!-- notes-slide -->
<!-- SLIDE_BOUNDARY -->
"""
        
        self.parser.parse_directives(content)
        
        # Check malformed directive suggestions
        suggestions = [m['suggestion'] for m in self.parser.malformed_directives]
        
        # Should suggest corrections
        assert '<!-- SLIDE -->' in suggestions
        assert '<!-- NOTES -->' in suggestions
    
    def test_notes_directive_validation(self):
        """Test validation warnings for NOTES directive usage."""
        content = """
<!-- SLIDE-ONLY -->
Some slides content.

<!-- NOTES -->
This should warn about nested mode.
"""
        
        directives = self.parser.parse_directives(content)
        warnings = self.parser.validate_directive_structure(directives)
        
        # Should have a warning about NOTES directive while in SLIDES_ONLY mode
        assert len(warnings) >= 1
        assert any("NOTES directive while already in" in warning for warning in warnings)
    
    def test_complete_workflow_with_new_directives(self):
        """Test complete workflow using new directive features."""
        content = """
# Lecture: Advanced Topics

This is the introduction that appears everywhere.

<!-- SLIDE -->
## First Topic

Key points for slides.

<!-- NOTES -->
## Detailed Notes Section

This section provides comprehensive details that students can read later.
It includes extended explanations and references.

The NOTES directive both starts a new slide boundary and makes content notes-only.

<!-- slides -->
## Another Slide (lowercase)

This tests case-insensitive slides directive.

<!-- ALL -->
## Conclusion

This conclusion appears in both slides and notes.
"""
        
        # Test the complete splitting process
        result = self.splitter.process_directives(content)
        
        slides_content = result["slides"]
        notes_content = result["notes"]
        
        # Verify slides content
        assert "This is the introduction" in slides_content
        assert "Key points for slides" in slides_content
        assert "Another Slide (lowercase)" in slides_content  
        assert "This conclusion appears" in slides_content
        
        # Notes-only content should NOT appear in slides
        assert "Detailed Notes Section" not in slides_content
        assert "comprehensive details" not in slides_content
        
        # Verify notes content (should have everything)
        assert "This is the introduction" in notes_content
        assert "Key points for slides" in notes_content
        assert "Detailed Notes Section" in notes_content
        assert "comprehensive details" in notes_content
        assert "Another Slide (lowercase)" in notes_content
        assert "This conclusion appears" in notes_content
        
        # Check slide boundaries
        assert len(self.splitter.slide_boundaries) == 3  # SLIDE, NOTES, slides


if __name__ == "__main__":
    pytest.main([__file__])