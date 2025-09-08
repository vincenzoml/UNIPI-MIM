"""
Tests for the markdown directive parser.

Tests the robust parsing of special markdown comments and state machine
implementation for content mode tracking.
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


if __name__ == "__main__":
    pytest.main([__file__])