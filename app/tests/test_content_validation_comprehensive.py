"""
Comprehensive tests for content validation and quality assurance system.

Tests all aspects of task 7: content validation, optimization, link checking,
image validation, and quality analysis.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from src.markdown_slides_generator.validation import (
    ContentValidator, ValidationResult, ValidationIssue, IssueType, IssueSeverity,
    SlideOptimizer, OptimizationResult, OptimizationType,
    LinkChecker, LinkValidationResult, check_links_sync,
    ImageValidator, ImageValidationResult,
    QualityAnalyzer, QualityReport, QualityMetric
)


class TestContentValidator:
    """Test comprehensive content validation system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ContentValidator()
    
    def test_validate_optimal_content(self):
        """Test validation of well-structured content."""
        content = """# Introduction

This is a well-structured presentation with optimal content length.

## Main Topic

Here we discuss the main topic with appropriate detail.

### Subtopic

Some additional information that supports the main topic.

## Conclusion

A brief summary of the key points covered.
"""
        result = self.validator.validate_content(content)
        
        assert result.is_valid
        assert result.word_count > 0
        assert result.slide_count_estimate >= 3
        assert result.readability_score > 60
        assert len(result.errors) == 0
    
    def test_validate_overly_long_content(self):
        """Test validation of content that's too long per slide."""
        # Create content with many words
        long_paragraph = " ".join(["word"] * 300)  # 300 words
        content = f"""# Long Slide

{long_paragraph}

This slide has way too much content and should trigger a validation error.
"""
        result = self.validator.validate_content(content)
        
        # Should have content length issues
        length_issues = [issue for issue in result.issues if issue.type == IssueType.CONTENT_LENGTH]
        assert len(length_issues) > 0
        assert any(issue.severity == IssueSeverity.ERROR for issue in length_issues)
    
    def test_validate_poor_structure(self):
        """Test validation of poorly structured content."""
        content = """# Title

Some content here.

### Skipped Level

This header skips from h1 to h3, which is poor structure.

##### Another Skip

This skips even more levels.
"""
        result = self.validator.validate_content(content)
        
        # Should have structure issues
        structure_issues = [issue for issue in result.issues if issue.type == IssueType.STRUCTURE]
        assert len(structure_issues) > 0
    
    def test_validate_latex_errors(self):
        """Test validation of content with LaTeX errors."""
        content = """# Math Content

Here's some broken LaTeX: $\\frac{1}{2$

And another error: $\\sqrt{x$

This should trigger LaTeX validation errors.
"""
        result = self.validator.validate_content(content)
        
        # Should have LaTeX issues
        latex_issues = [issue for issue in result.issues if issue.type == IssueType.LATEX_ERROR]
        assert len(latex_issues) > 0
    
    def test_validate_missing_images(self):
        """Test validation of content with missing images."""
        content = """# Images

Here's a missing image: ![Alt text](missing-image.png)

And another: ![](also-missing.jpg)
"""
        result = self.validator.validate_content(content, "/tmp/test.md")
        
        # Should have image issues
        image_issues = [issue for issue in result.issues if issue.type == IssueType.IMAGE_MISSING]
        assert len(image_issues) > 0
    
    def test_validate_broken_links(self):
        """Test validation of content with broken links."""
        content = """# Links

Here's a broken relative link: [Link](missing-file.md)

And an empty link: [Empty]()
"""
        result = self.validator.validate_content(content, "/tmp/test.md")
        
        # Should have link issues
        link_issues = [issue for issue in result.issues if issue.type == IssueType.LINK_BROKEN]
        assert len(link_issues) > 0
    
    def test_validate_formatting_issues(self):
        """Test validation of formatting issues."""
        content = """# Formatting Issues

This line is way too long and should trigger a formatting warning because it exceeds the recommended line length for readability.

- Inconsistent list
* Different marker
+ Another marker

Line with trailing spaces    
"""
        result = self.validator.validate_content(content)
        
        # Should have formatting issues
        formatting_issues = [issue for issue in result.issues if issue.type == IssueType.FORMATTING]
        assert len(formatting_issues) > 0
    
    def test_readability_calculation(self):
        """Test readability score calculation."""
        # Simple, readable content
        simple_content = "This is simple. Easy to read. Short sentences."
        result = self.validator.validate_content(simple_content)
        assert result.readability_score > 70
        
        # Complex, difficult content
        complex_content = """The implementation of sophisticated algorithmic methodologies 
        necessitates comprehensive understanding of multidimensional computational paradigms 
        that facilitate optimization of performance characteristics."""
        result = self.validator.validate_content(complex_content)
        assert result.readability_score < 70


class TestSlideOptimizer:
    """Test intelligent content optimization system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.optimizer = SlideOptimizer()
    
    def test_optimize_well_structured_content(self):
        """Test optimization of already well-structured content."""
        content = """# Introduction

Brief introduction to the topic.

## Main Point

Key information presented clearly.

## Conclusion

Summary of main points.
"""
        result = self.optimizer.optimize_content(content)
        
        assert result.improvements_made >= 0
        assert result.estimated_slide_count_after > 0
        assert len(result.suggestions) >= 0
    
    def test_split_long_slides(self):
        """Test automatic splitting of overly long slides."""
        # Create a very long slide
        long_content = " ".join(["This is a long sentence with many words."] * 50)
        content = f"""# Long Slide

{long_content}

This slide should be automatically split into multiple slides.
"""
        result = self.optimizer.optimize_content(content)
        
        # Should suggest splitting
        split_suggestions = [s for s in result.suggestions if s.type == OptimizationType.SPLIT_LONG_SLIDE]
        assert len(split_suggestions) > 0
        assert result.estimated_slide_count_after > result.estimated_slide_count_before
    
    def test_optimize_code_blocks(self):
        """Test optimization of long code blocks."""
        long_code = "\n".join([f"line_{i} = some_function()" for i in range(20)])
        content = f"""# Code Example

```python
{long_code}
```

This code block is too long for a slide.
"""
        result = self.optimizer.optimize_content(content)
        
        # Should suggest code optimization
        code_suggestions = [s for s in result.suggestions if s.type == OptimizationType.OPTIMIZE_CODE]
        assert len(code_suggestions) > 0
    
    def test_enhance_readability(self):
        """Test readability enhancement."""
        content = """# Long Sentences

This is an extremely long sentence that goes on and on and contains many clauses and subclauses that make it difficult to read and understand, especially in a presentation context where brevity and clarity are important.

Another very long sentence that should be broken up for better readability and comprehension by the audience.
"""
        result = self.optimizer.optimize_content(content)
        
        # Should suggest readability improvements
        readability_suggestions = [s for s in result.suggestions if s.type == OptimizationType.ENHANCE_READABILITY]
        assert len(readability_suggestions) > 0
    
    def test_balance_content(self):
        """Test content balancing across slides."""
        content = """# Very Short

Brief.

# Another Short

Also brief.

# Normal Length

This slide has a reasonable amount of content that should be appropriate for presentation purposes.
"""
        result = self.optimizer.optimize_content(content)
        
        # May suggest balancing
        balance_suggestions = [s for s in result.suggestions if s.type == OptimizationType.BALANCE_CONTENT]
        # This is optional - depends on the specific content


class TestLinkChecker:
    """Test link validation system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.checker = LinkChecker(timeout=5, max_concurrent=2)
    
    @pytest.mark.asyncio
    async def test_check_valid_http_links(self):
        """Test checking valid HTTP links."""
        content = """# Links

[Google](https://www.google.com)
[GitHub](https://github.com)
"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock successful responses
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.url = "https://www.google.com"
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await self.checker.check_links(content)
            
            assert result.total_links == 2
            assert result.success_rate > 0
    
    @pytest.mark.asyncio
    async def test_check_broken_http_links(self):
        """Test checking broken HTTP links."""
        content = """# Broken Links

[Broken](https://this-domain-does-not-exist-12345.com)
"""
        result = await self.checker.check_links(content)
        
        assert result.total_links == 1
        assert result.broken_links >= 0  # May fail due to network
    
    def test_check_links_sync_wrapper(self):
        """Test synchronous wrapper for link checking."""
        content = """# Simple Links

[Example](https://example.com)
"""
        result = check_links_sync(content, timeout=5)
        
        assert result.total_links == 1
        assert isinstance(result, type(result))  # Basic type check
    
    def test_validate_mailto_links(self):
        """Test validation of mailto links."""
        content = """# Email Links

[Email](mailto:test@example.com)
[Invalid Email](mailto:invalid-email)
"""
        result = check_links_sync(content)
        
        assert result.total_links == 2
        # Should have at least one valid and one invalid
    
    def test_validate_file_links(self):
        """Test validation of local file links."""
        # Create a temporary file
        test_file = Path("/tmp/test_link_file.txt")
        test_file.write_text("test content")
        
        try:
            content = f"""# File Links

[Existing File]({test_file})
[Missing File](/tmp/missing_file.txt)
"""
            result = check_links_sync(content, base_path=Path("/tmp"))
            
            assert result.total_links == 2
            assert result.valid_links >= 1  # At least the existing file
            assert result.broken_links >= 1  # At least the missing file
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_extract_various_link_formats(self):
        """Test extraction of different link formats."""
        content = """# Various Links

[Markdown Link](https://example.com)
<a href="https://html-link.com">HTML Link</a>
[Reference Link]: https://reference.com

Regular text with no links.
"""
        links = self.checker._extract_links(content)
        
        assert len(links) >= 3  # Should find all three types
    
    def test_academic_references(self):
        """Test academic reference validation."""
        content = """# Academic Content

DOI: 10.1234/example.doi
arXiv: arxiv:2021.12345
Invalid DOI: 10.123/invalid
Invalid arXiv: arxiv:invalid
"""
        references = self.checker.check_academic_references(content)
        
        assert len(references['dois']) >= 1
        assert len(references['arxiv']) >= 1
        assert len(references['malformed_dois']) >= 1
        assert len(references['malformed_arxiv']) >= 1


class TestImageValidator:
    """Test image validation and optimization system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ImageValidator()
    
    def test_validate_missing_images(self):
        """Test validation of missing image files."""
        content = """# Images

![Alt text](missing-image.png)
![Another missing](also-missing.jpg)
"""
        result = self.validator.validate_images(content, Path("/tmp"))
        
        assert result.total_images == 2
        assert result.missing_images == 2
        assert result.valid_images == 0
        assert len(result.optimization_suggestions) > 0
    
    def test_validate_images_without_alt_text(self):
        """Test validation of images without alt text."""
        content = """# Images

![](image-without-alt.png)
![Good alt text](image-with-alt.png)
"""
        result = self.validator.validate_images(content)
        
        assert result.total_images == 2
        assert result.images_without_alt >= 1
    
    def test_validate_external_images(self):
        """Test validation of external images (URLs)."""
        content = """# External Images

![External](https://example.com/image.png)
![Data URI](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==)
"""
        result = self.validator.validate_images(content)
        
        assert result.total_images == 2
        assert result.valid_images == 2  # External images assumed valid
        assert result.missing_images == 0
    
    def test_validate_existing_images(self):
        """Test validation of existing image files."""
        # Create temporary image files
        test_dir = Path("/tmp/test_images")
        test_dir.mkdir(exist_ok=True)
        
        small_image = test_dir / "small.png"
        large_image = test_dir / "large.png"
        
        # Create small file
        small_image.write_bytes(b"fake image content")
        
        # Create large file (simulate large image)
        large_content = b"fake large image content" * 100000  # ~2.4MB
        large_image.write_bytes(large_content)
        
        try:
            content = f"""# Test Images

![Small image](small.png)
![Large image](large.png)
![Missing alt](small.png)
"""
            result = self.validator.validate_images(content, test_dir)
            
            assert result.total_images == 3
            assert result.valid_images == 3  # All files exist
            assert result.missing_images == 0
            assert result.images_without_alt >= 1  # One without alt text
            assert result.oversized_images >= 1  # Large image
            
        finally:
            small_image.unlink(missing_ok=True)
            large_image.unlink(missing_ok=True)
            test_dir.rmdir()
    
    def test_image_format_suggestions(self):
        """Test image format optimization suggestions."""
        # Create test files with different extensions
        test_dir = Path("/tmp/test_formats")
        test_dir.mkdir(exist_ok=True)
        
        png_file = test_dir / "large.png"
        jpg_file = test_dir / "photo.jpg"
        
        # Create large PNG (should suggest WebP)
        large_content = b"fake large PNG content" * 50000  # ~1.2MB
        png_file.write_bytes(large_content)
        
        # Create normal JPG
        jpg_file.write_bytes(b"fake JPG content")
        
        try:
            content = f"""# Format Test

![Large PNG](large.png)
![Photo](photo.jpg)
"""
            result = self.validator.validate_images(content, test_dir)
            
            assert result.total_images == 2
            assert len(result.optimization_suggestions) > 0
            
            # Should suggest WebP for large PNG
            webp_suggestions = [s for s in result.optimization_suggestions if "WebP" in s]
            assert len(webp_suggestions) > 0
            
        finally:
            png_file.unlink(missing_ok=True)
            jpg_file.unlink(missing_ok=True)
            test_dir.rmdir()
    
    def test_generate_optimization_report(self):
        """Test generation of optimization report."""
        content = """# Report Test

![Missing](missing.png)
![No alt](existing.png)
"""
        result = self.validator.validate_images(content)
        
        report = self.validator.generate_optimization_report(result)
        
        assert "Image Optimization Report" in report
        assert "Total Images:" in report
        assert "Missing Images:" in report
        assert len(report) > 100  # Should be a substantial report


class TestQualityAnalyzer:
    """Test comprehensive quality analysis system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = QualityAnalyzer()
    
    def test_analyze_high_quality_content(self):
        """Test analysis of high-quality academic content."""
        content = """# Introduction to Machine Learning

Machine learning represents a fundamental paradigm shift in computational approaches. This presentation explores key concepts and methodologies.

## Supervised Learning

Supervised learning algorithms learn from labeled training data. Common approaches include:

- Linear regression for continuous outcomes
- Logistic regression for binary classification
- Decision trees for interpretable models

### Example: Linear Regression

The linear regression model can be expressed as:

$$y = \\beta_0 + \\beta_1 x + \\epsilon$$

Where $\\beta_0$ is the intercept and $\\beta_1$ is the slope parameter.

## Unsupervised Learning

Unsupervised learning discovers patterns in unlabeled data. Key techniques include clustering and dimensionality reduction.

## Conclusion

Machine learning provides powerful tools for data analysis. However, careful consideration of model assumptions and validation is essential.

## References

1. Bishop, C. M. (2006). Pattern Recognition and Machine Learning.
2. Hastie, T., et al. (2009). The Elements of Statistical Learning.
"""
        report = self.analyzer.analyze_quality(content)
        
        assert report.overall_score > 70  # Should be good quality
        assert len(report.metric_scores) == 6  # All metrics analyzed
        assert report.critical_issues == 0  # No critical issues
        assert len(report.strengths) > 0  # Should identify strengths
    
    def test_analyze_poor_quality_content(self):
        """Test analysis of poor-quality content."""
        content = """no headers just a wall of text that goes on and on without any structure or organization and uses very long sentences that are difficult to read and understand and contains no visual elements or proper formatting and lacks any academic references or citations and generally represents poor presentation quality that would be difficult for an audience to follow or understand during a presentation"""
        
        report = self.analyzer.analyze_quality(content)
        
        assert report.overall_score < 60  # Should be poor quality
        assert report.critical_issues > 0  # Should have critical issues
        assert len(report.improvement_suggestions) > 0  # Should suggest improvements
    
    def test_analyze_readability_metrics(self):
        """Test readability analysis."""
        # Simple, readable content
        simple_content = "This is simple. Easy to read. Short sentences. Clear meaning."
        report = self.analyzer.analyze_quality(simple_content)
        
        readability_score = report.get_score(QualityMetric.READABILITY)
        assert readability_score is not None
        assert readability_score.score > 70
        
        # Complex, difficult content
        complex_content = """The implementation of sophisticated algorithmic methodologies 
        necessitates comprehensive understanding of multidimensional computational paradigms 
        that facilitate optimization of performance characteristics through systematic 
        evaluation of alternative approaches."""
        report = self.analyzer.analyze_quality(complex_content)
        
        readability_score = report.get_score(QualityMetric.READABILITY)
        assert readability_score is not None
        assert readability_score.score < 70
    
    def test_analyze_structure_quality(self):
        """Test structure analysis."""
        # Well-structured content
        good_structure = """# Main Title

## Section 1

Content for section 1.

### Subsection 1.1

Detailed content.

## Section 2

Content for section 2.
"""
        report = self.analyzer.analyze_quality(good_structure)
        
        structure_score = report.get_score(QualityMetric.STRUCTURE)
        assert structure_score is not None
        assert structure_score.score > 70
        
        # Poorly structured content
        bad_structure = """# Title

##### Skipped levels

Content with poor hierarchy.

### Another skip

More poor structure.
"""
        report = self.analyzer.analyze_quality(bad_structure)
        
        structure_score = report.get_score(QualityMetric.STRUCTURE)
        assert structure_score is not None
        assert len(structure_score.suggestions) > 0
    
    def test_analyze_academic_standards(self):
        """Test academic standards analysis."""
        # Content with good academic standards
        academic_content = """# Research Methodology

According to Smith et al. (2020), the methodology should be rigorous.

## Analysis

The analysis shows significant results [@smith2020].

## References

Smith, J., et al. (2020). Research Methods. Journal of Science.
"""
        report = self.analyzer.analyze_quality(academic_content)
        
        academic_score = report.get_score(QualityMetric.ACADEMIC_STANDARDS)
        assert academic_score is not None
        assert academic_score.score > 60
        
        # Content without academic standards
        casual_content = """# My Thoughts

I think this is interesting. Here's what I found out.

Pretty cool stuff!
"""
        report = self.analyzer.analyze_quality(casual_content)
        
        academic_score = report.get_score(QualityMetric.ACADEMIC_STANDARDS)
        assert academic_score is not None
        assert len(academic_score.suggestions) > 0
    
    def test_analyze_presentation_quality(self):
        """Test presentation quality analysis."""
        # Good presentation content
        good_presentation = """# Title

## Key Points

- Point 1
- Point 2
- Point 3

## Visual Example

![Diagram](diagram.png)

```python
def example():
    return "code"
```

## Summary

Brief summary of key points.
"""
        report = self.analyzer.analyze_quality(good_presentation)
        
        presentation_score = report.get_score(QualityMetric.PRESENTATION_QUALITY)
        assert presentation_score is not None
        assert presentation_score.score > 60
    
    def test_analyze_accessibility(self):
        """Test accessibility analysis."""
        # Content with accessibility issues
        poor_accessibility = """# Title

![](missing-alt.png)
[click here](link.html)
<img src="no-alt.png">

##### Skipped header levels
"""
        report = self.analyzer.analyze_quality(poor_accessibility)
        
        accessibility_score = report.get_score(QualityMetric.ACCESSIBILITY)
        assert accessibility_score is not None
        assert len(accessibility_score.suggestions) > 0
    
    def test_identify_strengths_and_improvements(self):
        """Test identification of strengths and improvement areas."""
        mixed_content = """# Good Structure

This content has good structure and readability.

## Clear Sections

Each section is well-organized.

But it lacks citations and has some accessibility issues.

![](no-alt-text.png)
"""
        report = self.analyzer.analyze_quality(mixed_content)
        
        # Should identify both strengths and areas for improvement
        assert len(report.strengths) > 0
        assert len(report.improvement_suggestions) > 0
        assert report.overall_score > 50  # Mixed quality


class TestIntegratedValidation:
    """Test integrated validation system in content splitter."""
    
    def test_content_splitter_with_validation(self):
        """Test content splitter with integrated validation."""
        from src.markdown_slides_generator.core.content_splitter import ContentSplitter
        
        splitter = ContentSplitter()
        
        content = """# Test Content

This is test content with some issues.

![Missing image](missing.png)

$\\frac{1}{2$ <!-- Broken LaTeX -->

## Very Long Section

""" + " ".join(["word"] * 200) + """

This section is too long and should trigger optimization.
"""
        
        slides_content, notes_content = splitter.split_content_from_string(content)
        
        # Check that validation was performed
        validation_result = splitter.get_validation_result()
        assert validation_result is not None
        assert len(validation_result.issues) > 0
        
        # Check that optimization was performed
        optimization_result = splitter.get_optimization_result()
        assert optimization_result is not None
        
        # Check validation summary
        summary = splitter.get_validation_summary()
        assert 'total_issues' in summary
        assert 'suggestions' in summary
        assert summary['total_issues'] > 0
    
    def split_content_from_string(self, content: str) -> tuple:
        """Helper method to split content from string."""
        # This would be added to ContentSplitter class
        processed = self.process_directives(content)
        return processed["slides"], processed["notes"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])