#!/usr/bin/env python3
"""
Test script to verify that slide-only content doesn't appear in notes output.
"""

import sys
import os
sys.path.insert(0, '/Users/vincenzo/data/local/repos/UNIPI-MIM/app/src')

from markdown_slides_generator.core.content_splitter import ContentSplitter

def test_slide_only_not_in_notes():
    """Test that SLIDES_ONLY content does not appear in notes output."""
    
    test_content = """# Test Document

<!-- NOTES -->
This is notes-only content that should appear only in notes.

<!-- SLIDE -->
This is slide-only content that should appear only in slides.

<!-- ALL -->
This is ALL content that should appear in both slides and notes.

<!-- NOTES-ONLY -->
This is another notes-only section.
"""

    splitter = ContentSplitter()
    result = splitter.process_directives(test_content)
    
    slides_output = result['slides']
    notes_output = result['notes']
    
    print("=== SLIDES OUTPUT ===")
    print(slides_output)
    print("\n=== NOTES OUTPUT ===")
    print(notes_output)
    
    # Check that slide-only content is NOT in notes
    assert "This is slide-only content" not in notes_output, "SLIDE content should not appear in notes!"
    
    # Check that slide-only content IS in slides
    assert "This is slide-only content" in slides_output, "SLIDE content should appear in slides!"
    
    # Check that notes-only content is NOT in slides
    assert "This is notes-only content" not in slides_output, "NOTES content should not appear in slides!"
    assert "This is another notes-only section" not in slides_output, "NOTES-ONLY content should not appear in slides!"
    
    # Check that notes-only content IS in notes
    assert "This is notes-only content" in notes_output, "NOTES content should appear in notes!"
    assert "This is another notes-only section" in notes_output, "NOTES-ONLY content should appear in notes!"
    
    # Check that ALL content appears in both
    assert "This is ALL content" in slides_output, "ALL content should appear in slides!"
    assert "This is ALL content" in notes_output, "ALL content should appear in notes!"
    
    print("\n✅ All tests passed! Slide-only content is properly separated from notes.")

if __name__ == "__main__":
    test_slide_only_not_in_notes()
