"""
Quality Analyzer - Comprehensive content quality analysis.

Analyzes content structure, readability, academic standards,
and provides detailed quality reports with improvement suggestions.
"""

import re
import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..utils.logger import get_logger
from ..utils.exceptions import handle_exception

logger = get_logger(__name__)


class QualityMetric(Enum):
    """Quality metrics for content analysis."""
    READABILITY = "readability"
    STRUCTURE = "structure"
    CONSISTENCY = "consistency"
    ACCESSIBILITY = "accessibility"
    ACADEMIC_STANDARDS = "academic_standards"
    PRESENTATION_QUALITY = "presentation_quality"


@dataclass
class QualityScore:
    """Quality score for a specific metric."""
    metric: QualityMetric
    score: float  # 0.0 to 100.0
    details: Dict[str, Any]
    suggestions: List[str]


@dataclass
class QualityReport:
    """Comprehensive quality analysis report."""
    overall_score: float
    metric_scores: List[QualityScore]
    total_issues: int
    critical_issues: int
    improvement_suggestions: List[str]
    strengths: List[str]
    
    def get_score(self, metric: QualityMetric) -> Optional[QualityScore]:
        """Get score for a specific metric."""
        for score in self.metric_scores:
            if score.metric == metric:
                return score
        return None


class QualityAnalyzer:
    """
    Comprehensive content quality analysis system.
    
    Analyzes content across multiple dimensions including readability,
    structure, consistency, accessibility, and academic standards.
    """
    
    # Quality thresholds
    EXCELLENT_THRESHOLD = 90.0
    GOOD_THRESHOLD = 75.0
    ACCEPTABLE_THRESHOLD = 60.0
    
    # Text analysis patterns
    SENTENCE_PATTERN = re.compile(r'[.!?]+')
    WORD_PATTERN = re.compile(r'\b\w+\b')
    HEADER_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    LIST_PATTERN = re.compile(r'^(\s*)([-*+]|\d+\.)\s+(.+)$', re.MULTILINE)
    CODE_BLOCK_PATTERN = re.compile(r'```[\s\S]*?```', re.MULTILINE)
    LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    
    # Academic patterns
    CITATION_PATTERN = re.compile(r'\[@[^\]]+\]|\[[^\]]*\d{4}[^\]]*\]')
    REFERENCE_PATTERN = re.compile(r'^##?\s*(References?|Bibliography)', re.MULTILINE | re.IGNORECASE)
    
    def __init__(self):
        self.analysis_cache: Dict[str, Any] = {}
    
    @handle_exception
    def analyze_quality(self, content: str) -> QualityReport:
        """
        Perform comprehensive quality analysis.
        
        Args:
            content: Markdown content to analyze
            
        Returns:
            QualityReport with detailed analysis results
        """
        logger.info("Starting comprehensive quality analysis")
        
        # Clear cache for new analysis
        self.analysis_cache = {}
        
        # Analyze each quality metric
        metric_scores = [
            self._analyze_readability(content),
            self._analyze_structure(content),
            self._analyze_consistency(content),
            self._analyze_accessibility(content),
            self._analyze_academic_standards(content),
            self._analyze_presentation_quality(content)
        ]
        
        # Calculate overall score
        overall_score = sum(score.score for score in metric_scores) / len(metric_scores)
        
        # Collect issues and suggestions
        total_issues = sum(len(score.suggestions) for score in metric_scores)
        critical_issues = sum(1 for score in metric_scores if score.score < self.ACCEPTABLE_THRESHOLD)
        
        # Generate improvement suggestions
        improvement_suggestions = self._generate_improvement_suggestions(metric_scores)
        
        # Identify strengths
        strengths = self._identify_strengths(metric_scores)
        
        report = QualityReport(
            overall_score=overall_score,
            metric_scores=metric_scores,
            total_issues=total_issues,
            critical_issues=critical_issues,
            improvement_suggestions=improvement_suggestions,
            strengths=strengths
        )
        
        logger.info(f"Quality analysis complete: Overall score {overall_score:.1f}, "
                   f"{total_issues} issues, {critical_issues} critical")
        
        return report
    
    def _analyze_readability(self, content: str) -> QualityScore:
        """Analyze content readability."""
        # Remove code blocks and other non-prose content
        prose_content = self._extract_prose_content(content)
        
        if not prose_content.strip():
            return QualityScore(
                metric=QualityMetric.READABILITY,
                score=100.0,
                details={'reason': 'No prose content to analyze'},
                suggestions=[]
            )
        
        # Calculate readability metrics
        flesch_score = self._calculate_flesch_score(prose_content)
        avg_sentence_length = self._calculate_avg_sentence_length(prose_content)
        avg_word_length = self._calculate_avg_word_length(prose_content)
        complex_words_ratio = self._calculate_complex_words_ratio(prose_content)
        
        # Determine score based on Flesch Reading Ease
        if flesch_score >= 80:
            score = 95.0
        elif flesch_score >= 70:
            score = 85.0
        elif flesch_score >= 60:
            score = 75.0
        elif flesch_score >= 50:
            score = 65.0
        elif flesch_score >= 40:
            score = 55.0
        else:
            score = 45.0
        
        # Generate suggestions
        suggestions = []
        if avg_sentence_length > 25:
            suggestions.append("Consider breaking up long sentences for better readability")
        if complex_words_ratio > 0.15:
            suggestions.append("Consider using simpler vocabulary where possible")
        if flesch_score < 60:
            suggestions.append("Content may be difficult to read - consider simplifying language")
        
        details = {
            'flesch_score': flesch_score,
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length,
            'complex_words_ratio': complex_words_ratio
        }
        
        return QualityScore(
            metric=QualityMetric.READABILITY,
            score=score,
            details=details,
            suggestions=suggestions
        )
    
    def _analyze_structure(self, content: str) -> QualityScore:
        """Analyze content structure and organization."""
        headers = self.HEADER_PATTERN.findall(content)
        
        if not headers:
            return QualityScore(
                metric=QualityMetric.STRUCTURE,
                score=40.0,
                details={'headers': 0, 'hierarchy_issues': 1},
                suggestions=["Add headers to create clear content structure"]
            )
        
        # Analyze header hierarchy
        hierarchy_issues = 0
        prev_level = 0
        header_levels = []
        
        for header_markup, title in headers:
            level = len(header_markup)
            header_levels.append(level)
            
            if level > prev_level + 1:
                hierarchy_issues += 1
            
            prev_level = level
        
        # Check for balanced structure
        level_distribution = {}
        for level in header_levels:
            level_distribution[level] = level_distribution.get(level, 0) + 1
        
        # Calculate structure score
        base_score = 80.0
        
        # Deduct for hierarchy issues
        base_score -= hierarchy_issues * 10
        
        # Bonus for good structure
        if len(headers) >= 3 and hierarchy_issues == 0:
            base_score += 10
        
        # Ensure score is within bounds
        score = max(0, min(100, base_score))
        
        suggestions = []
        if hierarchy_issues > 0:
            suggestions.append("Fix header hierarchy - use sequential levels (h1 → h2 → h3)")
        if len(headers) < 3:
            suggestions.append("Consider adding more headers to improve content organization")
        
        # Check for very long titles
        long_titles = [title for _, title in headers if len(title) > 60]
        if long_titles:
            suggestions.append("Consider shortening long header titles for better readability")
        
        details = {
            'header_count': len(headers),
            'hierarchy_issues': hierarchy_issues,
            'level_distribution': level_distribution,
            'long_titles': len(long_titles)
        }
        
        return QualityScore(
            metric=QualityMetric.STRUCTURE,
            score=score,
            details=details,
            suggestions=suggestions
        )
    
    def _analyze_consistency(self, content: str) -> QualityScore:
        """Analyze content consistency."""
        issues = []
        
        # Check list marker consistency
        list_markers = self.LIST_PATTERN.findall(content)
        if list_markers:
            markers_used = set(marker for _, marker, _ in list_markers)
            if len(markers_used) > 2:
                issues.append("Inconsistent list markers used")
        
        # Check header formatting consistency
        headers = self.HEADER_PATTERN.findall(content)
        if headers:
            # Check for consistent capitalization
            title_case_count = sum(1 for _, title in headers if title.istitle())
            sentence_case_count = len(headers) - title_case_count
            
            if title_case_count > 0 and sentence_case_count > 0:
                issues.append("Inconsistent header capitalization")
        
        # Check link formatting
        links = self.LINK_PATTERN.findall(content)
        if links:
            # Check for consistent link text formatting
            empty_text_links = sum(1 for text, _ in links if not text.strip())
            if empty_text_links > 0:
                issues.append("Some links have empty or missing text")
        
        # Check code block language specification
        code_blocks = self.CODE_BLOCK_PATTERN.findall(content)
        if code_blocks:
            # This is a simplified check - would need more sophisticated parsing
            unspecified_languages = sum(1 for block in code_blocks if not block.strip().split('\n')[0])
            if unspecified_languages > len(code_blocks) / 2:
                issues.append("Many code blocks lack language specification")
        
        # Calculate consistency score
        base_score = 90.0
        score = max(0, base_score - len(issues) * 15)
        
        suggestions = []
        for issue in issues:
            suggestions.append(f"Fix consistency issue: {issue}")
        
        details = {
            'consistency_issues': len(issues),
            'issues': issues
        }
        
        return QualityScore(
            metric=QualityMetric.CONSISTENCY,
            score=score,
            details=details,
            suggestions=suggestions
        )
    
    def _analyze_accessibility(self, content: str) -> QualityScore:
        """Analyze content accessibility."""
        issues = []
        
        # Check images for alt text
        images = self.IMAGE_PATTERN.findall(content)
        missing_alt_text = sum(1 for alt, _ in images if not alt.strip())
        
        if missing_alt_text > 0:
            issues.append(f"{missing_alt_text} images missing alt text")
        
        # Check for very long alt text
        long_alt_text = sum(1 for alt, _ in images if len(alt) > 125)
        if long_alt_text > 0:
            issues.append(f"{long_alt_text} images have overly long alt text")
        
        # Check for descriptive link text
        links = self.LINK_PATTERN.findall(content)
        generic_link_text = sum(1 for text, _ in links 
                              if text.lower().strip() in ['click here', 'here', 'link', 'read more'])
        
        if generic_link_text > 0:
            issues.append(f"{generic_link_text} links use generic text")
        
        # Check for proper heading structure (accessibility requirement)
        headers = self.HEADER_PATTERN.findall(content)
        if headers:
            levels = [len(markup) for markup, _ in headers]
            if levels and levels[0] != 1:
                issues.append("Content should start with h1 header")
        
        # Calculate accessibility score
        total_elements = len(images) + len(links) + len(headers)
        if total_elements == 0:
            score = 100.0  # No accessibility elements to check
        else:
            issue_ratio = len(issues) / max(1, total_elements)
            score = max(0, 100 - issue_ratio * 100)
        
        suggestions = []
        for issue in issues:
            suggestions.append(f"Improve accessibility: {issue}")
        
        details = {
            'accessibility_issues': len(issues),
            'images_checked': len(images),
            'links_checked': len(links),
            'headers_checked': len(headers)
        }
        
        return QualityScore(
            metric=QualityMetric.ACCESSIBILITY,
            score=score,
            details=details,
            suggestions=suggestions
        )
    
    def _analyze_academic_standards(self, content: str) -> QualityScore:
        """Analyze adherence to academic standards."""
        issues = []
        strengths = []
        
        # Check for citations
        citations = self.CITATION_PATTERN.findall(content)
        if citations:
            strengths.append(f"Contains {len(citations)} citations")
        else:
            issues.append("No citations found - consider adding references")
        
        # Check for references section
        has_references = bool(self.REFERENCE_PATTERN.search(content))
        if has_references:
            strengths.append("Contains references section")
        elif citations:
            issues.append("Citations present but no references section found")
        
        # Check for academic language patterns
        academic_indicators = [
            r'\b(however|therefore|furthermore|moreover|consequently)\b',
            r'\b(according to|as shown by|research indicates)\b',
            r'\b(hypothesis|methodology|analysis|conclusion)\b'
        ]
        
        academic_language_count = 0
        for pattern in academic_indicators:
            academic_language_count += len(re.findall(pattern, content, re.IGNORECASE))
        
        if academic_language_count > 5:
            strengths.append("Uses appropriate academic language")
        elif academic_language_count < 2:
            issues.append("Consider using more formal academic language")
        
        # Check for proper figure/table references
        figure_refs = re.findall(r'Figure\s+\d+|Fig\.\s+\d+', content, re.IGNORECASE)
        table_refs = re.findall(r'Table\s+\d+', content, re.IGNORECASE)
        
        if figure_refs or table_refs:
            strengths.append("Uses proper figure/table references")
        
        # Calculate academic standards score
        base_score = 70.0
        base_score += len(strengths) * 5
        base_score -= len(issues) * 10
        
        score = max(0, min(100, base_score))
        
        suggestions = []
        for issue in issues:
            suggestions.append(f"Academic standard: {issue}")
        
        details = {
            'citations_count': len(citations),
            'has_references': has_references,
            'academic_language_indicators': academic_language_count,
            'strengths': strengths,
            'issues': issues
        }
        
        return QualityScore(
            metric=QualityMetric.ACADEMIC_STANDARDS,
            score=score,
            details=details,
            suggestions=suggestions
        )
    
    def _analyze_presentation_quality(self, content: str) -> QualityScore:
        """Analyze quality for presentation purposes."""
        issues = []
        
        # Estimate content density
        word_count = len(self.WORD_PATTERN.findall(content))
        headers = self.HEADER_PATTERN.findall(content)
        estimated_slides = max(1, len(headers))
        words_per_slide = word_count / estimated_slides
        
        if words_per_slide > 150:
            issues.append(f"Content may be too dense ({words_per_slide:.0f} words per slide)")
        elif words_per_slide < 20:
            issues.append(f"Content may be too sparse ({words_per_slide:.0f} words per slide)")
        
        # Check for visual elements
        images = self.IMAGE_PATTERN.findall(content)
        code_blocks = self.CODE_BLOCK_PATTERN.findall(content)
        lists = self.LIST_PATTERN.findall(content)
        
        visual_elements = len(images) + len(code_blocks) + len(lists)
        visual_ratio = visual_elements / max(1, estimated_slides)
        
        if visual_ratio < 0.5:
            issues.append("Consider adding more visual elements (images, code, lists)")
        
        # Check for very long code blocks
        long_code_blocks = 0
        for block in code_blocks:
            lines = block.count('\n')
            if lines > 15:
                long_code_blocks += 1
        
        if long_code_blocks > 0:
            issues.append(f"{long_code_blocks} code blocks may be too long for slides")
        
        # Calculate presentation quality score
        base_score = 80.0
        base_score -= len(issues) * 12
        
        # Bonus for good visual balance
        if 0.5 <= visual_ratio <= 2.0:
            base_score += 10
        
        score = max(0, min(100, base_score))
        
        suggestions = []
        for issue in issues:
            suggestions.append(f"Presentation quality: {issue}")
        
        details = {
            'estimated_slides': estimated_slides,
            'words_per_slide': words_per_slide,
            'visual_elements': visual_elements,
            'visual_ratio': visual_ratio,
            'presentation_issues': len(issues)
        }
        
        return QualityScore(
            metric=QualityMetric.PRESENTATION_QUALITY,
            score=score,
            details=details,
            suggestions=suggestions
        )
    
    def _extract_prose_content(self, content: str) -> str:
        """Extract prose content for readability analysis."""
        # Remove code blocks
        content = self.CODE_BLOCK_PATTERN.sub('', content)
        
        # Remove headers
        content = self.HEADER_PATTERN.sub('', content)
        
        # Remove links (keep text)
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
        
        # Remove images
        content = self.IMAGE_PATTERN.sub('', content)
        
        # Remove markdown formatting
        content = re.sub(r'[*_`]', '', content)
        
        return content.strip()
    
    def _calculate_flesch_score(self, text: str) -> float:
        """Calculate Flesch Reading Ease score."""
        sentences = len(self.SENTENCE_PATTERN.findall(text))
        words = self.WORD_PATTERN.findall(text)
        word_count = len(words)
        
        if word_count == 0 or sentences == 0:
            return 100.0
        
        # Estimate syllables
        syllable_count = sum(self._count_syllables(word) for word in words)
        
        # Flesch Reading Ease formula
        score = 206.835 - (1.015 * (word_count / sentences)) - (84.6 * (syllable_count / word_count))
        return max(0, min(100, score))
    
    def _calculate_avg_sentence_length(self, text: str) -> float:
        """Calculate average sentence length in words."""
        sentences = self.SENTENCE_PATTERN.split(text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        total_words = sum(len(self.WORD_PATTERN.findall(sentence)) for sentence in sentences)
        return total_words / len(sentences)
    
    def _calculate_avg_word_length(self, text: str) -> float:
        """Calculate average word length in characters."""
        words = self.WORD_PATTERN.findall(text)
        if not words:
            return 0.0
        
        total_chars = sum(len(word) for word in words)
        return total_chars / len(words)
    
    def _calculate_complex_words_ratio(self, text: str) -> float:
        """Calculate ratio of complex words (3+ syllables)."""
        words = self.WORD_PATTERN.findall(text)
        if not words:
            return 0.0
        
        complex_words = sum(1 for word in words if self._count_syllables(word) >= 3)
        return complex_words / len(words)
    
    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count for a word."""
        word = word.lower().strip('.,!?;:"')
        if not word:
            return 0
        
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
    
    def _generate_improvement_suggestions(self, metric_scores: List[QualityScore]) -> List[str]:
        """Generate prioritized improvement suggestions."""
        all_suggestions = []
        
        # Prioritize by score (lowest first)
        sorted_scores = sorted(metric_scores, key=lambda x: x.score)
        
        for score in sorted_scores:
            if score.score < self.GOOD_THRESHOLD:
                all_suggestions.extend(score.suggestions)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for suggestion in all_suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:10]  # Limit to top 10 suggestions
    
    def _identify_strengths(self, metric_scores: List[QualityScore]) -> List[str]:
        """Identify content strengths."""
        strengths = []
        
        for score in metric_scores:
            if score.score >= self.EXCELLENT_THRESHOLD:
                strengths.append(f"Excellent {score.metric.value} (score: {score.score:.1f})")
            elif score.score >= self.GOOD_THRESHOLD:
                strengths.append(f"Good {score.metric.value} (score: {score.score:.1f})")
        
        return strengths