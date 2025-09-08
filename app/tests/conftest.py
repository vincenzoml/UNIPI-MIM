"""
Pytest configuration and shared fixtures.
"""

import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_markdown():
    """Sample markdown content for testing."""
    return """# Test Lecture

This is a test lecture with some content.

## Section 1

Some content here.

<!-- SLIDE -->
## New Slide

This is slide content.

<!-- NOTES-ONLY -->
This is notes-only content.

<!-- ALL -->
Back to normal content.

## Math Example

Inline math: $E = mc^2$

Display math:
$$\\int_0^1 x^2 dx = \\frac{1}{3}$$
"""


@pytest.fixture
def sample_markdown_file(temp_dir, sample_markdown):
    """Create a temporary markdown file for testing."""
    markdown_file = temp_dir / "test_lecture.md"
    markdown_file.write_text(sample_markdown)
    return markdown_file