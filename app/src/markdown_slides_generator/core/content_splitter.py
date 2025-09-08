"""
Content Splitter - Sophisticated markdown directive parser and content router.

Implements a robust state machine to parse special markdown comments and
intelligently split content for slides and notes generation.
"""

import re
from enum import Enum
from typing import Tuple, List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import yaml

from ..utils.logger import get_logger
from ..utils.exceptions import handle_exception, InputError

logger = get_logger(__name__)


class ContentMode(Enum):
    """Content inclusion modes based on markdown directives."""
    ALL = "all"  # Content appears in both slides and notes
    SLIDES_ONLY = "slides_only"  # Content appears only in slides
    NOTES_ONLY = "notes_only"  # Content appears only in notes
    SLIDE_BOUNDARY = "slide_boundary"  # Marks a new slide boundary


@dataclass
class DirectiveMatch:
    """Represents a matched directive in the markdown content."""
    directive: str
    mode: ContentMode
    line_number: int
    position: int
    raw_match: str


@dataclass
class ContentBlock:
    """Represents a block of content with its associated mode."""
    content: str
    mode: ContentMode
    start_line: int
    end_line: int
    is_slide_boundary: bool = False
    header_level: Optional[int] = None


@dataclass
class SlideSection:
    """Represents a logical slide section with content and metadata."""
    title: str
    content: str
    slide_number: int
    header_level: int
    has_code: bool = False
    has_math: bool = False
    word_count: int = 0


class MarkdownDirectiveParser:
    """
    Robust parser for markdown directives with state machine implementation.
    
    Handles special comments:
    - <!-- SLIDE --> : Creates slide boundary
    - <!-- SLIDE-ONLY --> : Content only in slides
    - <!-- NOTES-ONLY --> : Content only in notes  
    - <!-- ALL --> : Content in both (return to normal)
    """
    
    # Directive patterns - case insensitive with flexible whitespace
    DIRECTIVE_PATTERNS = {
        r'<!--\s*SLIDE\s*-->': ContentMode.SLIDE_BOUNDARY,
        r'<!--\s*SLIDE-ONLY\s*-->': ContentMode.SLIDES_ONLY,
        r'<!--\s*NOTES-ONLY\s*-->': ContentMode.NOTES_ONLY,
        r'<!--\s*ALL\s*-->': ContentMode.ALL,
    }
    
    def __init__(self):
        self.current_mode = ContentMode.ALL
        self.directive_stack = []  # For tracking nested directives
        self.malformed_directives = []
        
    def parse_directives(self, content: str) -> List[DirectiveMatch]:
        """
        Parse all directives in the markdown content.
        
        Args:
            content: Raw markdown content
            
        Returns:
            List of DirectiveMatch objects in order of appearance
        """
        directives = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Find all directive matches in this line
            for pattern, mode in self.DIRECTIVE_PATTERNS.items():
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    directive = DirectiveMatch(
                        directive=match.group().strip(),
                        mode=mode,
                        line_number=line_num,
                        position=match.start(),
                        raw_match=match.group()
                    )
                    directives.append(directive)
                    logger.debug(f"Found directive '{directive.directive}' at line {line_num}")
        
        # Check for malformed directives (HTML comments that look like directives but don't match)
        self._check_malformed_directives(content, lines)
        
        return sorted(directives, key=lambda d: (d.line_number, d.position))
    
    def _check_malformed_directives(self, content: str, lines: List[str]):
        """Check for malformed directives and log warnings."""
        # Look for HTML comments that might be malformed directives
        malformed_pattern = r'<!--\s*[A-Z-]+\s*-->'
        
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(malformed_pattern, line, re.IGNORECASE)
            for match in matches:
                directive_text = match.group().strip()
                # Check if it's not a valid directive
                is_valid = any(re.match(pattern, directive_text, re.IGNORECASE) 
                             for pattern in self.DIRECTIVE_PATTERNS.keys())
                
                if not is_valid and any(keyword in directive_text.upper() 
                                      for keyword in ['SLIDE', 'NOTE', 'ALL']):
                    self.malformed_directives.append({
                        'text': directive_text,
                        'line': line_num,
                        'suggestion': self._suggest_correction(directive_text)
                    })
                    logger.warning(f"Possible malformed directive at line {line_num}: {directive_text}")
    
    def _suggest_correction(self, malformed: str) -> str:
        """Suggest correction for malformed directive."""
        upper_text = malformed.upper()
        if 'SLIDE-ONLY' in upper_text or 'SLIDEONLY' in upper_text:
            return '<!-- SLIDE-ONLY -->'
        elif 'NOTES-ONLY' in upper_text or 'NOTESONLY' in upper_text:
            return '<!-- NOTES-ONLY -->'
        elif 'SLIDE' in upper_text:
            return '<!-- SLIDE -->'
        elif 'ALL' in upper_text:
            return '<!-- ALL -->'
        return '<!-- SLIDE -->'
    
    def process_content_blocks(self, content: str, directives: List[DirectiveMatch]) -> List[ContentBlock]:
        """
        Process content into blocks based on directives using state machine.
        
        Args:
            content: Raw markdown content
            directives: List of parsed directives
            
        Returns:
            List of ContentBlock objects with content and modes
        """
        if not directives:
            # No directives found, treat all content as ALL mode
            return [ContentBlock(
                content=content,
                mode=ContentMode.ALL,
                start_line=1,
                end_line=len(content.split('\n'))
            )]
        
        lines = content.split('\n')
        blocks = []
        current_mode = ContentMode.ALL
        current_block_start = 1
        
        # Add a sentinel directive at the end to process the final block
        final_directive = DirectiveMatch(
            directive="<!-- END -->",
            mode=ContentMode.ALL,
            line_number=len(lines) + 1,
            position=0,
            raw_match="<!-- END -->"
        )
        directives_with_end = directives + [final_directive]
        
        for i, directive in enumerate(directives_with_end):
            # Process content block before this directive
            if directive.line_number > current_block_start:
                block_lines = lines[current_block_start - 1:directive.line_number - 1]
                block_content = '\n'.join(block_lines).strip()
                
                if block_content:  # Only add non-empty blocks
                    blocks.append(ContentBlock(
                        content=block_content,
                        mode=current_mode,
                        start_line=current_block_start,
                        end_line=directive.line_number - 1
                    ))
            
            # Update state based on directive (except for the sentinel)
            if directive != final_directive:
                current_mode = self._update_state(current_mode, directive)
                current_block_start = directive.line_number + 1
        
        return blocks
    
    def _update_state(self, current_mode: ContentMode, directive: DirectiveMatch) -> ContentMode:
        """
        Update the state machine based on the directive.
        
        Args:
            current_mode: Current content mode
            directive: The directive that was encountered
            
        Returns:
            New content mode
        """
        new_mode = directive.mode
        
        # Handle state transitions
        if new_mode == ContentMode.SLIDE_BOUNDARY:
            # SLIDE directive doesn't change the content mode, just marks boundaries
            return current_mode
        else:
            # Direct mode changes
            logger.debug(f"State transition: {current_mode.value} -> {new_mode.value} at line {directive.line_number}")
            return new_mode
    
    def validate_directive_structure(self, directives: List[DirectiveMatch]) -> List[str]:
        """
        Validate the structure of directives and return any warnings.
        
        Args:
            directives: List of parsed directives
            
        Returns:
            List of validation warning messages
        """
        warnings = []
        mode_stack = []
        current_mode = ContentMode.ALL
        
        for directive in directives:
            if directive.mode in [ContentMode.SLIDES_ONLY, ContentMode.NOTES_ONLY]:
                # Entering a special mode
                if current_mode != ContentMode.ALL:
                    warnings.append(f"Line {directive.line_number}: Nested mode directive {directive.mode.value} "
                                  f"while already in {current_mode.value} mode")
                mode_stack.append((directive, current_mode))
                current_mode = directive.mode
                
            elif directive.mode == ContentMode.ALL:
                # Returning to ALL mode
                if mode_stack:
                    mode_stack.pop()
                    current_mode = ContentMode.ALL
                else:
                    warnings.append(f"Line {directive.line_number}: <!-- ALL --> without matching mode directive")
            
            # SLIDE_BOUNDARY doesn't change the mode stack
        
        # Check for unclosed mode directives
        if mode_stack:
            for unclosed_directive, _ in mode_stack:
                warnings.append(f"Line {unclosed_directive.line_number}: Unclosed {unclosed_directive.mode.value} directive")
        
        return warnings


class ContentSplitter:
    """
    Sophisticated content splitter with robust markdown directive parsing.
    
    Uses a state machine to parse special markdown comments and intelligently
    split content for slides and notes generation with proper error handling.
    """
    
    def __init__(self):
        self.parser = MarkdownDirectiveParser()
        self.slide_boundaries = []
        self.validation_warnings = []
    
    @handle_exception
    def split_content(self, filepath: str) -> Tuple[str, str]:
        """
        Split markdown content into slides and notes based on directives.
        
        Args:
            filepath: Path to markdown file
            
        Returns:
            Tuple of (slides_content, notes_content)
            
        Raises:
            InputError: If file cannot be read or processed
        """
        logger.info(f"Processing file: {filepath}")
        
        file_path = Path(filepath)
        if not file_path.exists():
            raise InputError(f"File not found: {filepath}")
        
        try:
            content = file_path.read_text(encoding='utf-8')
            logger.debug(f"Read {len(content)} characters from {filepath}")
            
            # Process the content using the directive parser
            processed = self.process_directives(content)
            
            return processed["slides"], processed["notes"]
            
        except Exception as e:
            raise InputError(f"Error processing file {filepath}: {e}")
    
    def process_directives(self, content: str) -> Dict[str, str]:
        """
        Process markdown directives and split content accordingly.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Dictionary with 'slides' and 'notes' content
        """
        logger.debug("Processing markdown directives")
        
        # Parse all directives in the content
        directives = self.parser.parse_directives(content)
        logger.info(f"Found {len(directives)} directives")
        
        # Validate directive structure
        self.validation_warnings = self.parser.validate_directive_structure(directives)
        for warning in self.validation_warnings:
            logger.warning(warning)
        
        # Report malformed directives
        for malformed in self.parser.malformed_directives:
            logger.warning(f"Malformed directive at line {malformed['line']}: {malformed['text']} "
                         f"(suggestion: {malformed['suggestion']})")
        
        # Process content into blocks
        content_blocks = self.parser.process_content_blocks(content, directives)
        logger.debug(f"Created {len(content_blocks)} content blocks")
        
        # Split content based on modes
        slides_blocks = []
        notes_blocks = []
        
        for block in content_blocks:
            if block.mode in [ContentMode.ALL, ContentMode.SLIDES_ONLY]:
                slides_blocks.append(block.content)
            if block.mode in [ContentMode.ALL, ContentMode.NOTES_ONLY]:
                notes_blocks.append(block.content)
        
        # Track slide boundaries for later use in task 2.2
        self.slide_boundaries = [d.line_number for d in directives 
                               if d.mode == ContentMode.SLIDE_BOUNDARY]
        
        slides_content = '\n\n'.join(slides_blocks).strip()
        notes_content = '\n\n'.join(notes_blocks).strip()
        
        logger.info(f"Generated slides content: {len(slides_content)} chars")
        logger.info(f"Generated notes content: {len(notes_content)} chars")
        
        return {
            "slides": slides_content,
            "notes": notes_content,
            "blocks": content_blocks,
            "directives": directives,
            "warnings": self.validation_warnings
        }
    
    def get_slide_boundaries(self) -> List[int]:
        """Get line numbers where slide boundaries were detected."""
        return self.slide_boundaries.copy()
    
    def get_validation_warnings(self) -> List[str]:
        """Get validation warnings from the last processing."""
        return self.validation_warnings.copy()
    
    def generate_quarto_files(self, filepath: str, output_dir: str = "output") -> Tuple[str, str]:
        """
        Generate clean Quarto .qmd files for slides and notes.
        
        Args:
            filepath: Path to input markdown file
            output_dir: Directory for output files
            
        Returns:
            Tuple of (slides_qmd_path, notes_qmd_path)
        """
        logger.info(f"Generating Quarto files from {filepath}")
        
        # Process the content
        file_path = Path(filepath)
        content = file_path.read_text(encoding='utf-8')
        processed = self.process_directives(content)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate file names
        base_name = file_path.stem
        slides_path = output_path / f"{base_name}_slides.qmd"
        notes_path = output_path / f"{base_name}_notes.qmd"
        
        # Generate slides content with intelligent splitting
        slides_content = self._generate_slides_qmd(processed, base_name)
        notes_content = self._generate_notes_qmd(processed, base_name)
        
        # Write files
        slides_path.write_text(slides_content, encoding='utf-8')
        notes_path.write_text(notes_content, encoding='utf-8')
        
        logger.info(f"Generated slides: {slides_path}")
        logger.info(f"Generated notes: {notes_path}")
        
        return str(slides_path), str(notes_path)
    
    def _generate_slides_qmd(self, processed: Dict[str, Any], title: str) -> str:
        """Generate Quarto slides file with proper YAML frontmatter."""
        
        # Analyze content for intelligent slide splitting
        slide_sections = self._create_intelligent_slides(processed["slides"])
        
        # Generate YAML frontmatter for slides
        yaml_config = {
            'title': title.replace('_', ' ').replace('-', ' ').title(),
            'format': {
                'revealjs': {
                    'theme': 'white',
                    'slide-number': True,
                    'chalkboard': True,
                    'preview-links': 'auto',
                    'logo': None,
                    'footer': None
                }
            },
            'editor': 'visual'
        }
        
        # Build the complete Quarto document
        yaml_header = "---\n" + yaml.dump(yaml_config, default_flow_style=False) + "---\n\n"
        
        # Process slides content with intelligent boundaries
        slides_body = self._format_slides_content(slide_sections)
        
        return yaml_header + slides_body
    
    def _generate_notes_qmd(self, processed: Dict[str, Any], title: str) -> str:
        """Generate Quarto notes file with academic formatting."""
        
        # Generate YAML frontmatter for notes
        yaml_config = {
            'title': title.replace('_', ' ').replace('-', ' ').title() + ' - Lecture Notes',
            'format': {
                'pdf': {
                    'documentclass': 'article',
                    'toc': True,
                    'number-sections': True,
                    'colorlinks': True,
                    'geometry': 'margin=1in'
                },
                'html': {
                    'toc': True,
                    'toc-depth': 3,
                    'number-sections': True,
                    'theme': 'cosmo'
                }
            },
            'editor': 'visual'
        }
        
        yaml_header = "---\n" + yaml.dump(yaml_config, default_flow_style=False) + "---\n\n"
        
        # Format notes content (preserve all structure)
        notes_body = self._format_notes_content(processed["notes"])
        
        return yaml_header + notes_body
    
    def _create_intelligent_slides(self, slides_content: str) -> List[SlideSection]:
        """
        Intelligently split content into slide sections based on structure.
        
        Args:
            slides_content: Raw slides content
            
        Returns:
            List of SlideSection objects
        """
        lines = slides_content.split('\n')
        sections = []
        current_section = None
        slide_number = 1
        
        for line in lines:
            # Check for headers (potential slide boundaries)
            header_match = re.match(r'^(#{1,6})\s+(.+)', line)
            
            if header_match:
                # Save previous section if exists
                if current_section and current_section.content.strip():
                    sections.append(current_section)
                    slide_number += 1
                
                # Start new section
                header_level = len(header_match.group(1))
                title = header_match.group(2)
                
                current_section = SlideSection(
                    title=title,
                    content=line + '\n',
                    slide_number=slide_number,
                    header_level=header_level
                )
            else:
                # Add to current section
                if current_section:
                    current_section.content += line + '\n'
                    
                    # Analyze content characteristics
                    if '```' in line:
                        current_section.has_code = True
                    if '$' in line and ('$' in line[line.index('$')+1:] if '$' in line else False):
                        current_section.has_math = True
                else:
                    # Content before first header - create intro section
                    if line.strip():
                        current_section = SlideSection(
                            title="Introduction",
                            content=line + '\n',
                            slide_number=slide_number,
                            header_level=1
                        )
        
        # Add final section
        if current_section and current_section.content.strip():
            sections.append(current_section)
        
        # Calculate word counts and optimize slide lengths
        for section in sections:
            section.word_count = len(section.content.split())
        
        return self._optimize_slide_lengths(sections)
    
    def _optimize_slide_lengths(self, sections: List[SlideSection]) -> List[SlideSection]:
        """
        Optimize slide lengths by splitting overly long slides.
        
        Args:
            sections: List of slide sections
            
        Returns:
            Optimized list of slide sections
        """
        optimized = []
        max_words_per_slide = 150  # Reasonable limit for slides
        
        for section in sections:
            if section.word_count <= max_words_per_slide:
                optimized.append(section)
            else:
                # Split long section
                logger.info(f"Splitting long slide '{section.title}' ({section.word_count} words)")
                split_sections = self._split_long_section(section, max_words_per_slide)
                optimized.extend(split_sections)
        
        return optimized
    
    def _split_long_section(self, section: SlideSection, max_words: int) -> List[SlideSection]:
        """Split a long section into multiple slides."""
        # Split content into words for more precise control
        words = section.content.split()
        split_sections = []
        current_words = []
        part_number = 1
        
        # Keep the header for the first part
        header_line = ""
        content_words = words
        
        # Extract header if present
        if section.content.startswith('#'):
            first_line_end = section.content.find('\n')
            if first_line_end > 0:
                header_line = section.content[:first_line_end]
                remaining_content = section.content[first_line_end+1:]
                content_words = remaining_content.split()
        
        for word in content_words:
            if len(current_words) >= max_words and current_words:
                # Create new section
                content = header_line + '\n\n' + ' '.join(current_words) if header_line else ' '.join(current_words)
                split_sections.append(SlideSection(
                    title=f"{section.title} ({part_number})",
                    content=content.strip(),
                    slide_number=section.slide_number,
                    header_level=section.header_level,
                    has_code=section.has_code,
                    has_math=section.has_math,
                    word_count=len(current_words)
                ))
                
                current_words = [word]
                part_number += 1
            else:
                current_words.append(word)
        
        # Add final part
        if current_words:
            content = header_line + '\n\n' + ' '.join(current_words) if header_line else ' '.join(current_words)
            split_sections.append(SlideSection(
                title=f"{section.title} ({part_number})" if part_number > 1 else section.title,
                content=content.strip(),
                slide_number=section.slide_number,
                header_level=section.header_level,
                has_code=section.has_code,
                has_math=section.has_math,
                word_count=len(current_words)
            ))
        
        return split_sections
    
    def _format_slides_content(self, sections: List[SlideSection]) -> str:
        """Format slide sections for Quarto reveal.js output."""
        formatted_content = []
        
        for i, section in enumerate(sections):
            # Add slide separator (except for first slide)
            if i > 0:
                formatted_content.append("\n---\n")
            
            # Add section content
            formatted_content.append(section.content.strip())
            
            # Add speaker notes if this is a complex slide
            if section.has_code or section.has_math or section.word_count > 100:
                formatted_content.append(f"\n::: {{.notes}}")
                formatted_content.append(f"This slide covers {section.title.lower()}.")
                if section.has_code:
                    formatted_content.append("Pay attention to the code examples.")
                if section.has_math:
                    formatted_content.append("Note the mathematical expressions.")
                formatted_content.append(":::")
        
        return '\n'.join(formatted_content)
    
    def _format_notes_content(self, notes_content: str) -> str:
        """Format notes content for academic PDF/HTML output."""
        # For notes, we preserve the full structure
        # Add any academic formatting enhancements here
        
        lines = notes_content.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Enhance headers for better academic formatting
            if re.match(r'^#{1,6}\s+', line):
                formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)