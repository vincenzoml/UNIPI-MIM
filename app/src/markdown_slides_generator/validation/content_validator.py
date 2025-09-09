"""
Content Validator - Comprehensive content validation system.

Validates slide content length, LaTeX expressions, links, images,
and provides automatic splitting suggestions for optimal presentation.
"""

import re
import math
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from ..utils.logger import get_logger
from ..utils.exceptions import handle_exception, InputError
from ..latex import LaTeXProcessor, LaTeXValidationResult

logger = get_logger(__name__)


class IssueType(Enum):
    """Types of validation issues."""
    CONTENT_LENGTH = "content_length"
    LATEX_ERROR = "latex_error"
    LINK_BROKEN = "link_broken"
    IMAGE_MISSING = "image_missing"
    IMAGE_SIZE = "image_size"
    READABILITY = "readability"
    STRUCTURE = "structure"
    FORMATTING = "formatting"


class IssueSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUGGESTION = "suggestion"


@dataclass
class ValidationIssue:
    """Represents a validation issue found in content."""
    type: IssueType
    severity: IssueSeverity
    message: str
    line_number: Optional[int] = None
    column: Optional[int] = None
    suggestion: Optional[str] = None
    context: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of content validation."""
    is_valid: bool
    issues: List[ValidationIssue]
    word_count: int
    slide_count_estimate: int
    readability_score: float
    latex_validation: Optional[LaTeXValidationResult] = None
    
    @property
    def errors(self) -> List[ValidationIssue]:
        """Get only error-level issues."""
        return [issue for issue in self.issues if issue.severity == IssueSeverity.ERROR]
    
    @property
    def warnings(self) -> List[ValidationIssue]:
        """Get only warning-level issues."""
        return [issue for issue in self.issues if issue.severity == IssueSeverity.WARNING]
    
    @property
    def suggestions(self) -> List[ValidationIssue]:
        """Get only suggestion-level issues."""
        return [issue for issue in self.issues if issue.severity == IssueSeverity.SUGGESTION]


class ContentValidator:
    """
    Comprehensive content validation system for academic presentations.
    
    Validates content length, LaTeX expressions, links, images, and provides
    suggestions for improving slide readability and structure.
    """
    
    # Content length thresholds (words per slide)
    OPTIMAL_WORDS_PER_SLIDE = 50
    MAX_WORDS_PER_SLIDE = 150
    CRITICAL_WORDS_PER_SLIDE = 250
    
    # Readability thresholds
    MIN_READABILITY_SCORE = 60  # Flesch Reading Ease
    OPTIMAL_READABILITY_SCORE = 70
    
    # Structure validation patterns
    HEADER_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    CODE_BLOCK_PATTERN = re.compile(r'```[\s\S]*?```', re.MULTILINE)
    INLINE_CODE_PATTERN = re.compile(r'`[^`]+`')
    LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    LATEX_INLINE_PATTERN = re.compile(r'\$[^$]+\$')
    LATEX_BLOCK_PATTERN = re.compile(r'\$\$[\s\S]*?\$\$')
    
    def __init__(self):
        self.latex_processor = LaTeXProcessor()
        self.issues: List[ValidationIssue] = []
    
    @handle_exception
    def validate_content(self, content: str, filepath: Optional[str] = None) -> ValidationResult:
        """
        Perform comprehensive content validation.
        
        Args:
            content: Markdown content to validate
            filepath: Optional path to the source file
            
        Returns:
            ValidationResult with all validation findings
        """
        logger.info("Starting comprehensive content validation")
        self.issues = []
        
        # Basic content analysis
        word_count = self._count_words(content)
        slide_count = self._estimate_slide_count(content)
        readability_score = self._calculate_readability(content)
        
        # Validate content length and structure
        self._validate_content_length(content, slide_count)
        self._validate_structure(content)
        self._validate_readability(content, readability_score)
        
        # Validate LaTeX expressions
        latex_result = self._validate_latex_expressions(content)
        
        # Validate links and images
        self._validate_links(content, filepath)
        self._validate_images(content, filepath)
        
        # Check formatting and style
        self._validate_formatting(content)
        
        # Determine overall validity
        has_errors = any(issue.severity == IssueSeverity.ERROR for issue in self.issues)
        
        result = ValidationResult(
            is_valid=not has_errors,
            issues=self.issues.copy(),
            word_count=word_count,
            slide_count_estimate=slide_count,
            readability_score=readability_score,
            latex_validation=latex_result
        )
        
        logger.info(f"Validation complete: {len(result.errors)} errors, "
                   f"{len(result.warnings)} warnings, {len(result.suggestions)} suggestions")
        
        return result
    
    def _count_words(self, content: str) -> int:
        """Count words in content, excluding code blocks and LaTeX."""
        # Remove code blocks
        content_no_code = self.CODE_BLOCK_PATTERN.sub('', content)
        content_no_code = self.INLINE_CODE_PATTERN.sub('', content_no_code)
        
        # Remove LaTeX expressions
        content_no_latex = self.LATEX_BLOCK_PATTERN.sub('', content_no_code)
        content_no_latex = self.LATEX_INLINE_PATTERN.sub('', content_no_latex)
        
        # Remove markdown formatting
        content_clean = re.sub(r'[#*_`\[\]()]', ' ', content_no_latex)
        
        # Count words
        words = content_clean.split()
        return len([word for word in words if word.strip()])
    
    def _estimate_slide_count(self, content: str) -> int:
        """Estimate number of slides based on headers and content."""
        # Count headers (potential slide boundaries)
        headers = self.HEADER_PATTERN.findall(content)
        header_count = len(headers)
        
        # If no headers, estimate based on content length
        if header_count == 0:
            word_count = self._count_words(content)
            return max(1, math.ceil(word_count / self.OPTIMAL_WORDS_PER_SLIDE))
        
        return max(1, header_count)
    
    def _calculate_readability(self, content: str) -> float:
        """Calculate Flesch Reading Ease score."""
        # Remove code blocks and LaTeX for readability analysis
        text = self.CODE_BLOCK_PATTERN.sub('', content)
        text = self.LATEX_BLOCK_PATTERN.sub('', text)
        text = self.LATEX_INLINE_PATTERN.sub('', text)
        
        # Remove markdown formatting
        text = re.sub(r'[#*_`\[\]()]', ' ', text)
        
        # Count sentences and syllables
        sentences = len(re.findall(r'[.!?]+', text))
        words = text.split()
        word_count = len(words)
        
        if word_count == 0 or sentences == 0:
            return 100.0  # Perfect score for empty content
        
        # Estimate syllables (simplified)
        syllable_count = sum(self._count_syllables(word) for word in words)
        
        # Flesch Reading Ease formula
        if sentences > 0 and word_count > 0:
            score = 206.835 - (1.015 * (word_count / sentences)) - (84.6 * (syllable_count / word_count))
            return max(0, min(100, score))
        
        return 100.0
    
    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count for a word."""
        word = word.lower().strip('.,!?;:"')
        if not word:
            return 0
        
        # Simple syllable counting heuristic
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _validate_content_length(self, content: str, slide_count: int):
        """Validate content length and suggest splitting if needed."""
        word_count = self._count_words(content)
        avg_words_per_slide = word_count / slide_count if slide_count > 0 else word_count
        
        if avg_words_per_slide > self.CRITICAL_WORDS_PER_SLIDE:
            self.issues.append(ValidationIssue(
                type=IssueType.CONTENT_LENGTH,
                severity=IssueSeverity.ERROR,
                message=f"Content is too dense: {avg_words_per_slide:.0f} words per slide "
                       f"(critical threshold: {self.CRITICAL_WORDS_PER_SLIDE})",
                suggestion="Consider breaking content into more slides or removing non-essential details"
            ))
        elif avg_words_per_slide > self.MAX_WORDS_PER_SLIDE:
            self.issues.append(ValidationIssue(
                type=IssueType.CONTENT_LENGTH,
                severity=IssueSeverity.WARNING,
                message=f"Content may be too dense: {avg_words_per_slide:.0f} words per slide "
                       f"(recommended max: {self.MAX_WORDS_PER_SLIDE})",
                suggestion="Consider using bullet points or splitting into additional slides"
            ))
        elif avg_words_per_slide > self.OPTIMAL_WORDS_PER_SLIDE:
            self.issues.append(ValidationIssue(
                type=IssueType.CONTENT_LENGTH,
                severity=IssueSeverity.SUGGESTION,
                message=f"Content could be more concise: {avg_words_per_slide:.0f} words per slide "
                       f"(optimal: {self.OPTIMAL_WORDS_PER_SLIDE})",
                suggestion="Consider using more visual elements or bullet points"
            ))
    
    def _validate_structure(self, content: str):
        """Validate content structure and hierarchy."""
        lines = content.split('\n')
        headers = []
        
        for line_num, line in enumerate(lines, 1):
            header_match = self.HEADER_PATTERN.match(line)
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                headers.append((level, title, line_num))
        
        # Check for proper header hierarchy
        if headers:
            prev_level = 0
            for level, title, line_num in headers:
                if level > prev_level + 1:
                    self.issues.append(ValidationIssue(
                        type=IssueType.STRUCTURE,
                        severity=IssueSeverity.WARNING,
                        message=f"Header level jump from {prev_level} to {level}",
                        line_number=line_num,
                        suggestion="Use sequential header levels (h1 → h2 → h3) for better structure"
                    ))
                
                # Check for very long titles
                if len(title) > 80:
                    self.issues.append(ValidationIssue(
                        type=IssueType.STRUCTURE,
                        severity=IssueSeverity.SUGGESTION,
                        message=f"Header title is very long ({len(title)} characters)",
                        line_number=line_num,
                        suggestion="Consider shortening the header for better slide readability"
                    ))
                
                prev_level = level
        else:
            # No headers found
            word_count = self._count_words(content)
            if word_count > self.MAX_WORDS_PER_SLIDE:
                self.issues.append(ValidationIssue(
                    type=IssueType.STRUCTURE,
                    severity=IssueSeverity.WARNING,
                    message="No headers found in content with substantial text",
                    suggestion="Add headers to create logical slide boundaries"
                ))
    
    def _validate_readability(self, content: str, readability_score: float):
        """Validate content readability."""
        if readability_score < self.MIN_READABILITY_SCORE:
            self.issues.append(ValidationIssue(
                type=IssueType.READABILITY,
                severity=IssueSeverity.WARNING,
                message=f"Content may be difficult to read (score: {readability_score:.1f})",
                suggestion="Consider using shorter sentences and simpler vocabulary"
            ))
        elif readability_score < self.OPTIMAL_READABILITY_SCORE:
            self.issues.append(ValidationIssue(
                type=IssueType.READABILITY,
                severity=IssueSeverity.SUGGESTION,
                message=f"Content readability could be improved (score: {readability_score:.1f})",
                suggestion="Consider breaking up long sentences and using active voice"
            ))
    
    def _validate_latex_expressions(self, content: str) -> Optional[LaTeXValidationResult]:
        """Validate LaTeX expressions in content."""
        try:
            latex_result = self.latex_processor.process_content(content)
            
            # Convert LaTeX errors to validation issues
            for error in latex_result.errors:
                self.issues.append(ValidationIssue(
                    type=IssueType.LATEX_ERROR,
                    severity=IssueSeverity.ERROR,
                    message=f"LaTeX error: {error}",
                    suggestion="Check LaTeX syntax and ensure all braces are balanced"
                ))
            
            # Convert LaTeX warnings to validation issues
            for warning in latex_result.warnings:
                self.issues.append(ValidationIssue(
                    type=IssueType.LATEX_ERROR,
                    severity=IssueSeverity.WARNING,
                    message=f"LaTeX warning: {warning}",
                    suggestion="Review LaTeX expression for potential issues"
                ))
            
            return latex_result
            
        except Exception as e:
            self.issues.append(ValidationIssue(
                type=IssueType.LATEX_ERROR,
                severity=IssueSeverity.ERROR,
                message=f"LaTeX validation failed: {e}",
                suggestion="Check LaTeX expressions for syntax errors"
            ))
            return None
    
    def _validate_links(self, content: str, filepath: Optional[str]):
        """Validate links in content."""
        links = self.LINK_PATTERN.findall(content)
        
        for link_text, link_url in links:
            # Check for empty links
            if not link_url.strip():
                self.issues.append(ValidationIssue(
                    type=IssueType.LINK_BROKEN,
                    severity=IssueSeverity.ERROR,
                    message=f"Empty link URL for text '{link_text}'",
                    suggestion="Provide a valid URL for the link"
                ))
                continue
            
            # Check for relative file links
            if not link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                if filepath:
                    base_dir = Path(filepath).parent
                    link_path = base_dir / link_url
                    if not link_path.exists():
                        self.issues.append(ValidationIssue(
                            type=IssueType.LINK_BROKEN,
                            severity=IssueSeverity.ERROR,
                            message=f"Broken relative link: {link_url}",
                            suggestion="Check that the linked file exists or use an absolute URL"
                        ))
                else:
                    self.issues.append(ValidationIssue(
                        type=IssueType.LINK_BROKEN,
                        severity=IssueSeverity.WARNING,
                        message=f"Cannot verify relative link: {link_url}",
                        suggestion="Ensure the linked file exists in the correct location"
                    ))
    
    def _validate_images(self, content: str, filepath: Optional[str]):
        """Validate images in content."""
        images = self.IMAGE_PATTERN.findall(content)
        
        for alt_text, image_url in images:
            # Check for empty alt text
            if not alt_text.strip():
                self.issues.append(ValidationIssue(
                    type=IssueType.IMAGE_MISSING,
                    severity=IssueSeverity.WARNING,
                    message=f"Image missing alt text: {image_url}",
                    suggestion="Add descriptive alt text for accessibility"
                ))
            
            # Check for relative image paths
            if not image_url.startswith(('http://', 'https://', 'data:')):
                if filepath:
                    base_dir = Path(filepath).parent
                    image_path = base_dir / image_url
                    if not image_path.exists():
                        self.issues.append(ValidationIssue(
                            type=IssueType.IMAGE_MISSING,
                            severity=IssueSeverity.ERROR,
                            message=f"Image file not found: {image_url}",
                            suggestion="Check that the image file exists or use an absolute URL"
                        ))
                    else:
                        # Check image size if file exists
                        try:
                            file_size = image_path.stat().st_size
                            if file_size > 5 * 1024 * 1024:  # 5MB
                                self.issues.append(ValidationIssue(
                                    type=IssueType.IMAGE_SIZE,
                                    severity=IssueSeverity.WARNING,
                                    message=f"Large image file: {image_url} ({file_size / 1024 / 1024:.1f}MB)",
                                    suggestion="Consider optimizing image size for better performance"
                                ))
                        except OSError:
                            pass
                else:
                    self.issues.append(ValidationIssue(
                        type=IssueType.IMAGE_MISSING,
                        severity=IssueSeverity.WARNING,
                        message=f"Cannot verify image: {image_url}",
                        suggestion="Ensure the image file exists in the correct location"
                    ))
    
    def _validate_formatting(self, content: str):
        """Validate formatting and style issues."""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for very long lines
            if len(line) > 120:
                self.issues.append(ValidationIssue(
                    type=IssueType.FORMATTING,
                    severity=IssueSeverity.SUGGESTION,
                    message=f"Very long line ({len(line)} characters)",
                    line_number=line_num,
                    suggestion="Consider breaking long lines for better readability"
                ))
            
            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                self.issues.append(ValidationIssue(
                    type=IssueType.FORMATTING,
                    severity=IssueSeverity.INFO,
                    message="Line has trailing whitespace",
                    line_number=line_num,
                    suggestion="Remove trailing whitespace"
                ))
            
            # Check for inconsistent list formatting
            if re.match(r'^\s*[-*+]\s', line):
                # Check if previous line is also a list item with different marker
                if line_num > 1:
                    prev_line = lines[line_num - 2]
                    if re.match(r'^\s*[-*+]\s', prev_line):
                        current_marker = re.match(r'^\s*([-*+])', line).group(1)
                        prev_marker = re.match(r'^\s*([-*+])', prev_line).group(1)
                        if current_marker != prev_marker:
                            self.issues.append(ValidationIssue(
                                type=IssueType.FORMATTING,
                                severity=IssueSeverity.SUGGESTION,
                                message="Inconsistent list markers",
                                line_number=line_num,
                                suggestion="Use consistent list markers (-, *, or +) throughout"
                            ))