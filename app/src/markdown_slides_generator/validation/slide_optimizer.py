"""
Slide Optimizer - Intelligent content optimization and splitting.

Provides automatic slide splitting for overly long content, content flow
optimization, and suggestions for improving slide readability and structure.
"""

import re
import math
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from ..utils.logger import get_logger
from ..utils.exceptions import handle_exception

logger = get_logger(__name__)


class OptimizationType(Enum):
    """Types of content optimizations."""
    SPLIT_LONG_SLIDE = "split_long_slide"
    IMPROVE_FLOW = "improve_flow"
    ENHANCE_READABILITY = "enhance_readability"
    OPTIMIZE_CODE = "optimize_code"
    BALANCE_CONTENT = "balance_content"


@dataclass
class OptimizationSuggestion:
    """Represents an optimization suggestion."""
    type: OptimizationType
    description: str
    original_content: str
    optimized_content: str
    confidence: float  # 0.0 to 1.0
    reason: str


@dataclass
class OptimizationResult:
    """Result of content optimization."""
    original_content: str
    optimized_content: str
    suggestions: List[OptimizationSuggestion]
    improvements_made: int
    estimated_slide_count_before: int
    estimated_slide_count_after: int


class SlideOptimizer:
    """
    Intelligent content optimization system for academic presentations.
    
    Automatically splits overly long content, optimizes content flow between
    slides and notes, and provides suggestions for improving readability.
    """
    
    # Content optimization thresholds
    MAX_WORDS_PER_SLIDE = 150
    OPTIMAL_WORDS_PER_SLIDE = 75
    MIN_WORDS_PER_SLIDE = 20
    
    # Code block optimization
    MAX_LINES_PER_CODE_BLOCK = 15
    OPTIMAL_LINES_PER_CODE_BLOCK = 10
    
    # Patterns for content analysis
    HEADER_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    CODE_BLOCK_PATTERN = re.compile(r'```(\w+)?\n([\s\S]*?)```', re.MULTILINE)
    LIST_PATTERN = re.compile(r'^(\s*)([-*+]|\d+\.)\s+(.+)$', re.MULTILINE)
    PARAGRAPH_PATTERN = re.compile(r'\n\s*\n')
    
    def __init__(self):
        self.suggestions: List[OptimizationSuggestion] = []
    
    @handle_exception
    def optimize_content(self, content: str) -> OptimizationResult:
        """
        Perform comprehensive content optimization.
        
        Args:
            content: Original markdown content
            
        Returns:
            OptimizationResult with optimized content and suggestions
        """
        logger.info("Starting content optimization")
        self.suggestions = []
        
        original_slide_count = self._estimate_slide_count(content)
        optimized_content = content
        
        # Apply optimizations in order of importance
        optimized_content = self._split_long_slides(optimized_content)
        optimized_content = self._optimize_code_blocks(optimized_content)
        optimized_content = self._improve_content_flow(optimized_content)
        optimized_content = self._enhance_readability(optimized_content)
        optimized_content = self._balance_slide_content(optimized_content)
        
        final_slide_count = self._estimate_slide_count(optimized_content)
        
        result = OptimizationResult(
            original_content=content,
            optimized_content=optimized_content,
            suggestions=self.suggestions.copy(),
            improvements_made=len(self.suggestions),
            estimated_slide_count_before=original_slide_count,
            estimated_slide_count_after=final_slide_count
        )
        
        logger.info(f"Optimization complete: {len(self.suggestions)} improvements made, "
                   f"slide count: {original_slide_count} → {final_slide_count}")
        
        return result
    
    def _estimate_slide_count(self, content: str) -> int:
        """Estimate number of slides based on headers and content."""
        headers = self.HEADER_PATTERN.findall(content)
        if headers:
            return len(headers)
        
        # Estimate based on content length
        words = len(content.split())
        return max(1, math.ceil(words / self.OPTIMAL_WORDS_PER_SLIDE))
    
    def _split_long_slides(self, content: str) -> str:
        """Split overly long slides into multiple slides."""
        sections = self._parse_sections(content)
        optimized_sections = []
        
        for section in sections:
            word_count = len(section['content'].split())
            
            if word_count > self.MAX_WORDS_PER_SLIDE:
                # Split this section
                split_sections = self._split_section(section)
                optimized_sections.extend(split_sections)
                
                self.suggestions.append(OptimizationSuggestion(
                    type=OptimizationType.SPLIT_LONG_SLIDE,
                    description=f"Split long slide with {word_count} words into {len(split_sections)} slides",
                    original_content=section['content'],
                    optimized_content='\n\n'.join(s['content'] for s in split_sections),
                    confidence=0.9,
                    reason=f"Content exceeded {self.MAX_WORDS_PER_SLIDE} words per slide"
                ))
            else:
                optimized_sections.append(section)
        
        return self._reconstruct_content(optimized_sections)
    
    def _parse_sections(self, content: str) -> List[Dict[str, Any]]:
        """Parse content into logical sections."""
        sections = []
        lines = content.split('\n')
        current_section = {'header': '', 'level': 0, 'content': '', 'start_line': 0}
        
        for line_num, line in enumerate(lines):
            header_match = self.HEADER_PATTERN.match(line)
            
            if header_match:
                # Save previous section if it has content
                if current_section['content'].strip():
                    sections.append(current_section)
                
                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = {
                    'header': line,
                    'level': level,
                    'title': title,
                    'content': line + '\n',
                    'start_line': line_num
                }
            else:
                current_section['content'] += line + '\n'
        
        # Add final section
        if current_section['content'].strip():
            sections.append(current_section)
        
        # If no sections found, treat entire content as one section
        if not sections:
            sections.append({
                'header': '',
                'level': 0,
                'title': 'Content',
                'content': content,
                'start_line': 0
            })
        
        return sections
    
    def _split_section(self, section: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split a long section into multiple shorter sections."""
        content = section['content']
        header = section['header']
        title = section.get('title', 'Content')
        level = section.get('level', 1)
        
        # Remove header from content for splitting
        content_without_header = content
        if header:
            content_without_header = content.replace(header, '', 1).strip()
        
        # Split by paragraphs
        paragraphs = self.PARAGRAPH_PATTERN.split(content_without_header)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        if not paragraphs:
            return [section]  # Can't split further
        
        # Group paragraphs into slides
        slides = []
        current_slide_content = []
        current_word_count = 0
        
        for paragraph in paragraphs:
            paragraph_words = len(paragraph.split())
            
            if (current_word_count + paragraph_words > self.OPTIMAL_WORDS_PER_SLIDE and 
                current_slide_content):
                # Start new slide
                slides.append('\n\n'.join(current_slide_content))
                current_slide_content = [paragraph]
                current_word_count = paragraph_words
            else:
                current_slide_content.append(paragraph)
                current_word_count += paragraph_words
        
        # Add remaining content
        if current_slide_content:
            slides.append('\n\n'.join(current_slide_content))
        
        # Create new sections
        split_sections = []
        for i, slide_content in enumerate(slides):
            if i == 0:
                # First slide keeps original header
                new_content = header + '\n\n' + slide_content if header else slide_content
                new_title = title
            else:
                # Subsequent slides get numbered headers
                header_prefix = '#' * max(1, level)
                new_title = f"{title} ({i + 1})"
                new_content = f"{header_prefix} {new_title}\n\n{slide_content}"
            
            split_sections.append({
                'header': f"{'#' * max(1, level)} {new_title}" if i > 0 else header,
                'level': level,
                'title': new_title,
                'content': new_content,
                'start_line': section['start_line']
            })
        
        return split_sections
    
    def _optimize_code_blocks(self, content: str) -> str:
        """Optimize code blocks for better presentation."""
        def optimize_code_block(match):
            language = match.group(1) or ''
            code = match.group(2)
            lines = code.strip().split('\n')
            
            if len(lines) > self.MAX_LINES_PER_CODE_BLOCK:
                # Split long code blocks
                optimized_code = self._split_code_block(code, language)
                
                self.suggestions.append(OptimizationSuggestion(
                    type=OptimizationType.OPTIMIZE_CODE,
                    description=f"Split long code block ({len(lines)} lines) for better readability",
                    original_content=match.group(0),
                    optimized_content=optimized_code,
                    confidence=0.8,
                    reason=f"Code block exceeded {self.MAX_LINES_PER_CODE_BLOCK} lines"
                ))
                
                return optimized_code
            
            return match.group(0)
        
        return self.CODE_BLOCK_PATTERN.sub(optimize_code_block, content)
    
    def _split_code_block(self, code: str, language: str) -> str:
        """Split a long code block into multiple blocks with explanations."""
        lines = code.strip().split('\n')
        chunks = []
        current_chunk = []
        
        for line in lines:
            current_chunk.append(line)
            
            if len(current_chunk) >= self.OPTIMAL_LINES_PER_CODE_BLOCK:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
        
        # Add remaining lines
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        # Create multiple code blocks with explanatory text
        result_parts = []
        for i, chunk in enumerate(chunks):
            if i > 0:
                result_parts.append(f"\n<!-- SLIDE -->\n\n### Code (continued)\n\n")
            
            result_parts.append(f"```{language}\n{chunk}\n```")
        
        return ''.join(result_parts)
    
    def _improve_content_flow(self, content: str) -> str:
        """Improve content flow between slides."""
        sections = self._parse_sections(content)
        
        for i, section in enumerate(sections):
            if i > 0:  # Not the first section
                # Check if section needs better transition
                prev_section = sections[i - 1]
                if self._needs_transition(prev_section, section):
                    transition = self._generate_transition(prev_section, section)
                    section['content'] = transition + '\n\n' + section['content']
                    
                    self.suggestions.append(OptimizationSuggestion(
                        type=OptimizationType.IMPROVE_FLOW,
                        description="Added transition between slides for better flow",
                        original_content=section['content'],
                        optimized_content=section['content'],
                        confidence=0.7,
                        reason="Detected abrupt topic change between slides"
                    ))
        
        return self._reconstruct_content(sections)
    
    def _needs_transition(self, prev_section: Dict[str, Any], current_section: Dict[str, Any]) -> bool:
        """Check if a transition is needed between sections."""
        # Simple heuristic: different header levels or very different topics
        prev_level = prev_section.get('level', 1)
        current_level = current_section.get('level', 1)
        
        # If moving to a higher level (more general), might need transition
        return current_level < prev_level
    
    def _generate_transition(self, prev_section: Dict[str, Any], current_section: Dict[str, Any]) -> str:
        """Generate a transition comment between sections."""
        return "<!-- Transition: Moving to next topic -->"
    
    def _enhance_readability(self, content: str) -> str:
        """Enhance content readability."""
        lines = content.split('\n')
        enhanced_lines = []
        
        for line in lines:
            # Break up very long sentences
            if len(line) > 120 and not line.startswith('#') and not line.startswith('```'):
                enhanced_line = self._break_long_sentence(line)
                if enhanced_line != line:
                    self.suggestions.append(OptimizationSuggestion(
                        type=OptimizationType.ENHANCE_READABILITY,
                        description="Broke up long sentence for better readability",
                        original_content=line,
                        optimized_content=enhanced_line,
                        confidence=0.6,
                        reason="Sentence was too long for slide presentation"
                    ))
                    enhanced_lines.append(enhanced_line)
                else:
                    enhanced_lines.append(line)
            else:
                enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)
    
    def _break_long_sentence(self, sentence: str) -> str:
        """Break a long sentence into shorter, more readable parts."""
        # Simple approach: break at conjunctions and relative clauses
        break_points = [', and ', ', but ', ', or ', ', which ', ', that ', '; ']
        
        for break_point in break_points:
            if break_point in sentence and len(sentence) > 120:
                parts = sentence.split(break_point, 1)
                if len(parts) == 2 and len(parts[0]) > 30:
                    return parts[0] + '.\n\n' + parts[1].strip().capitalize()
        
        return sentence
    
    def _balance_slide_content(self, content: str) -> str:
        """Balance content across slides for better presentation."""
        sections = self._parse_sections(content)
        
        # Identify very short and very long sections
        short_sections = []
        long_sections = []
        
        for i, section in enumerate(sections):
            word_count = len(section['content'].split())
            if word_count < self.MIN_WORDS_PER_SLIDE:
                short_sections.append(i)
            elif word_count > self.MAX_WORDS_PER_SLIDE:
                long_sections.append(i)
        
        # Try to merge very short sections
        if len(short_sections) > 1:
            merged_sections = self._merge_short_sections(sections, short_sections)
            if merged_sections != sections:
                self.suggestions.append(OptimizationSuggestion(
                    type=OptimizationType.BALANCE_CONTENT,
                    description=f"Merged {len(short_sections)} short sections for better balance",
                    original_content="Multiple short sections",
                    optimized_content="Merged sections",
                    confidence=0.8,
                    reason="Multiple sections had insufficient content"
                ))
                sections = merged_sections
        
        return self._reconstruct_content(sections)
    
    def _merge_short_sections(self, sections: List[Dict[str, Any]], short_indices: List[int]) -> List[Dict[str, Any]]:
        """Merge short sections together."""
        if len(short_indices) < 2:
            return sections
        
        # Simple approach: merge consecutive short sections
        merged_sections = []
        i = 0
        
        while i < len(sections):
            if i in short_indices and i + 1 in short_indices:
                # Merge this section with the next one
                current = sections[i]
                next_section = sections[i + 1]
                
                merged_content = current['content'] + '\n\n' + next_section['content']
                merged_section = {
                    'header': current['header'],
                    'level': current['level'],
                    'title': current.get('title', 'Merged Content'),
                    'content': merged_content,
                    'start_line': current['start_line']
                }
                
                merged_sections.append(merged_section)
                i += 2  # Skip the next section as it's been merged
            else:
                merged_sections.append(sections[i])
                i += 1
        
        return merged_sections
    
    def _reconstruct_content(self, sections: List[Dict[str, Any]]) -> str:
        """Reconstruct content from sections."""
        return '\n\n'.join(section['content'] for section in sections)


class OptimizedContentSplitter:
    """
    Enhanced content splitter with optimization capabilities.
    
    Extends the basic content splitter with intelligent optimization
    and automatic quality improvements.
    """
    
    def __init__(self):
        self.optimizer = SlideOptimizer()
    
    def split_and_optimize_content(self, content: str) -> Tuple[str, str, OptimizationResult]:
        """
        Split content and apply optimizations.
        
        Args:
            content: Original markdown content
            
        Returns:
            Tuple of (optimized_slides_content, optimized_notes_content, optimization_result)
        """
        # First optimize the content
        optimization_result = self.optimizer.optimize_content(content)
        optimized_content = optimization_result.optimized_content
        
        # Then split the optimized content
        # For now, return the same content for both slides and notes
        # This would be enhanced with actual splitting logic
        slides_content = optimized_content
        notes_content = optimized_content
        
        return slides_content, notes_content, optimization_result