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
from ..latex import LaTeXProcessor
from ..validation import ContentValidator, SlideOptimizer, ValidationResult, OptimizationResult

logger = get_logger(__name__)


class ContentMode(Enum):
    """Content inclusion modes based on markdown directives."""
    ALL = "all"  # Content appears in both slides and notes
    SLIDES_ONLY = "slides_only"  # Content appears only in slides
    NOTES_ONLY = "notes_only"  # Content appears only in notes
    SLIDE_BOUNDARY = "slide_boundary"  # Marks a new slide boundary
    NOTES_SLIDE_BOUNDARY = "notes_slide_boundary"  # Marks a new slide boundary AND content is notes-only


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
    """Content block routed to slides/notes with associated mode and line span."""
    content: str
    mode: ContentMode
    start_line: int
    end_line: int


@dataclass
class SlideSection:
    title: str
    content: str
    slide_number: int
    header_level: int = 1
    has_code: bool = False
    has_math: bool = False
    word_count: int = 0


class MarkdownDirectiveParser:  # restore original class header (implementation below remains intact)
    # Directive regex patterns mapped to modes
    DIRECTIVE_PATTERNS: Dict[str, ContentMode] = {
        # Notes / end-of-slide synonyms (treated as notes-only + boundary)
        r'<!--\s*END\s*SLIDE-ONLY\s*-->': ContentMode.NOTES_ONLY,
        r'<!--\s*SLIDE\s*END-ONLY\s*-->': ContentMode.NOTES_ONLY,
        r'<!--\s*END\s*SLIDE\s*ONLY\s*-->': ContentMode.NOTES_ONLY,
        r'<!--\s*END\s*SLIDE\s*-->': ContentMode.NOTES_SLIDE_BOUNDARY,
        r'<!--\s*SLIDE\s*END\s*-->': ContentMode.NOTES_SLIDE_BOUNDARY,
        # Explicit notes directives
        r'<!--\s*NOTES-ONLY\s*-->': ContentMode.NOTES_ONLY,
        r'<!--\s*NOTES\s*-->': ContentMode.NOTES_SLIDE_BOUNDARY,  # acts as boundary + notes-only
        # Slide directives (keep generic slide patterns after END SLIDE patterns)
        r'<!--\s*SLIDE-ONLY\s*-->': ContentMode.SLIDES_ONLY,
        r'<!--\s*SLIDES-ONLY\s*-->': ContentMode.SLIDES_ONLY,
        r'<!--\s*SLIDES?\s*-->': ContentMode.SLIDES_ONLY,         # SLIDE or SLIDES now means slides only
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
        
        # Track code block state
        in_code_block = False
        code_block_fence = None
        
        for line_num, line in enumerate(lines, 1):
            # Check for code block boundaries
            stripped_line = line.strip()
            
            # Check for fenced code blocks (``` or ~~~)
            if stripped_line.startswith('```') or stripped_line.startswith('~~~'):
                if not in_code_block:
                    in_code_block = True
                    code_block_fence = stripped_line[:3]
                elif code_block_fence and stripped_line.startswith(code_block_fence):
                    in_code_block = False
                    code_block_fence = None
                continue
            
            # Skip directive parsing if we're inside a code block
            if in_code_block:
                continue
            
            # Check for inline code and skip directives inside backticks
            if '`' in line:
                # Find all directive matches and check if they're inside inline code
                for pattern, mode in self.DIRECTIVE_PATTERNS.items():
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        if not self._is_inside_inline_code(line, match.start(), match.end()):
                            directive = DirectiveMatch(
                                directive=match.group().strip(),
                                mode=mode,
                                line_number=line_num,
                                position=match.start(),
                                raw_match=match.group()
                            )
                            directives.append(directive)
                            logger.debug(f"Found directive '{directive.directive}' at line {line_num}")
            else:
                # No inline code, process normally
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
    
    def _is_inside_inline_code(self, line: str, start_pos: int, end_pos: int) -> bool:
        """Check if a position range is inside inline code (backticks)."""
        # Find all backtick pairs in the line
        backticks = []
        i = 0
        while i < len(line):
            if line[i] == '`':
                # Count consecutive backticks
                tick_count = 0
                start_tick = i
                while i < len(line) and line[i] == '`':
                    tick_count += 1
                    i += 1
                backticks.append((start_tick, i - 1, tick_count))
            else:
                i += 1
        
        # Match opening and closing backticks
        code_spans = []
        i = 0
        while i < len(backticks):
            start_tick_pos, start_tick_end, start_tick_count = backticks[i]
            # Find matching closing backticks
            for j in range(i + 1, len(backticks)):
                end_tick_pos, end_tick_end, end_tick_count = backticks[j]
                if end_tick_count == start_tick_count:
                    # Found matching pair
                    code_spans.append((start_tick_end + 1, end_tick_pos))
                    i = j + 1
                    break
            else:
                # No matching closing backticks found
                i += 1
        
        # Check if the directive position is inside any code span
        for code_start, code_end in code_spans:
            if code_start <= start_pos and end_pos <= code_end:
                return True
        
        return False
    
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
                                      for keyword in ['SLIDE', 'SLDIE', 'NOTE', 'ALL']):
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
        elif 'NOTE-ONLY' in upper_text or 'NOTEONLY' in upper_text:
            return '<!-- NOTES-ONLY -->'  # Suggest plural form
        elif 'SLIDES-ONLY' in upper_text:
            return '<!-- SLIDE-ONLY -->'  # Correct to singular form
        elif 'SLDIE' in upper_text:  # Common typo
            return '<!-- SLIDE -->'
        elif 'NOTES' in upper_text and ('SLIDE' in upper_text or 'BOUNDARY' in upper_text):
            return '<!-- NOTES -->'  # Suggest NOTES for notes + slide boundary
        elif 'NOTE' in upper_text and 'SLIDE' not in upper_text:
            return '<!-- NOTES -->'  # Suggest NOTES for general notes
        elif 'SLIDES' in upper_text or 'SLIDE' in upper_text:
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
        if new_mode == ContentMode.SLIDES_ONLY:
            # SLIDE/SLIDES directive transitions to slides-only mode
            logger.debug(f"State transition: {current_mode.value} -> SLIDES_ONLY (via SLIDE directive) at line {directive.line_number}")
            return ContentMode.SLIDES_ONLY
        elif new_mode == ContentMode.NOTES_SLIDE_BOUNDARY:
            # NOTES directive marks a slide boundary AND changes mode to notes-only
            logger.debug(f"State transition: {current_mode.value} -> notes_only (via NOTES boundary) at line {directive.line_number}")
            return ContentMode.NOTES_ONLY
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
                
            elif directive.mode == ContentMode.NOTES_SLIDE_BOUNDARY:
                # NOTES directive acts as slide boundary + notes-only mode
                if current_mode != ContentMode.ALL:
                    warnings.append(f"Line {directive.line_number}: NOTES directive while already in {current_mode.value} mode")
                mode_stack.append((directive, current_mode))
                current_mode = ContentMode.NOTES_ONLY
                
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
        self.latex_processor = LaTeXProcessor()
        self.content_validator = ContentValidator()
        self.slide_optimizer = SlideOptimizer()
        self.slide_boundaries = []
        self.validation_warnings = []
        self.latex_validation_result = None
        self.validation_result = None
        self.optimization_result = None
    
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
    
    def process_directives(self, content: str) -> Dict[str, Any]:
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
        
        # Validate LaTeX expressions in the content
        self.latex_validation_result = self.latex_processor.process_content(content)
        if not self.latex_validation_result.is_valid:
            logger.warning(f"Found {len(self.latex_validation_result.errors)} LaTeX errors")
            for error in self.latex_validation_result.errors:
                logger.error(f"LaTeX Error: {error}")
        
        if self.latex_validation_result.warnings:
            for warning in self.latex_validation_result.warnings:
                logger.warning(f"LaTeX Warning: {warning}")
        
        # Log LaTeX package requirements
        if self.latex_validation_result.packages_required:
            logger.info(f"Required LaTeX packages: {', '.join(sorted(self.latex_validation_result.packages_required))}")
        
        # Perform comprehensive content validation
        self.validation_result = self.content_validator.validate_content(content)
        if not self.validation_result.is_valid:
            logger.warning(f"Content validation found {len(self.validation_result.errors)} errors")
            for error in self.validation_result.errors:
                logger.error(f"Validation Error: {error.message}")
        
        if self.validation_result.warnings:
            logger.info(f"Content validation found {len(self.validation_result.warnings)} warnings")
        
        # Optimization system DISABLED - preserving manual slide separators
        logger.info("Optimization system disabled to preserve manual slide boundaries")
        self.optimization_result = None
        
        # Split content based on modes
        slides_blocks = []
        notes_blocks = []

        # Build a lookup for directives by line number for quick checks
        directives_by_line = {d.line_number: d for d in directives}

        # Insert separators BEFORE boundary directives instead of after blocks to prevent content bleed.
        boundary_lines = {d.line_number for d in directives if d.mode in (ContentMode.SLIDE_BOUNDARY, ContentMode.NOTES_SLIDE_BOUNDARY)}
        for block in content_blocks:
            # If this block starts immediately after a boundary directive, add separator (unless first slide)
            if (block.start_line - 1) in boundary_lines:
                if slides_blocks and slides_blocks[-1].strip() != '---':
                    slides_blocks.append('---')

            if block.mode == ContentMode.SLIDES_ONLY:
                slides_blocks.append(block.content)
            elif block.mode == ContentMode.NOTES_ONLY:
                notes_blocks.append(block.content)
            elif block.mode == ContentMode.ALL:
                slides_blocks.append(block.content)
                notes_blocks.append(block.content)
            elif block.mode == ContentMode.NOTES_SLIDE_BOUNDARY:
                # Boundary already handled; content (if any) only to notes
                if block.content.strip():
                    notes_blocks.append(block.content)
            elif block.mode == ContentMode.SLIDE_BOUNDARY:
                # Usually empty; if user placed content same line region treat as slide-only after separator
                if block.content.strip():
                    slides_blocks.append(block.content)

        # Track slide boundaries for later use in task 2.2
        self.slide_boundaries = [d.line_number for d in directives 
                               if d.mode in [ContentMode.SLIDE_BOUNDARY, ContentMode.NOTES_SLIDE_BOUNDARY]]

        # Join blocks into final markdown content. Keep separators as their own paragraphs.
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
    
    def get_latex_validation_result(self):
        """Get the LaTeX validation result from the last processing."""
        return self.latex_validation_result
    
    def get_required_latex_packages(self) -> List[str]:
        """Get the list of required LaTeX packages."""
        if self.latex_validation_result:
            return list(self.latex_validation_result.packages_required)
        return []
    
    def has_latex_errors(self) -> bool:
        """Check if there are any LaTeX validation errors."""
        return bool(self.latex_validation_result and not self.latex_validation_result.is_valid)
    
    def get_validation_result(self) -> Optional[ValidationResult]:
        """Get the content validation result from the last processing."""
        return self.validation_result
    
    def get_optimization_result(self) -> Optional[OptimizationResult]:
        """Get the content optimization result from the last processing."""
        return self.optimization_result
    
    def has_validation_errors(self) -> bool:
        """Check if there are any content validation errors."""
        return bool(self.validation_result and not self.validation_result.is_valid)
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of all validation results."""
        summary = {
            'latex_valid': self.latex_validation_result.is_valid if self.latex_validation_result else True,
            'content_valid': self.validation_result.is_valid if self.validation_result else True,
            'optimization_applied': self.optimization_result.improvements_made > 0 if self.optimization_result else False,
            'total_issues': 0,
            'suggestions': []
        }
        
        if self.latex_validation_result:
            summary['total_issues'] += len(self.latex_validation_result.errors) + len(self.latex_validation_result.warnings)
        
        if self.validation_result:
            summary['total_issues'] += len(self.validation_result.errors) + len(self.validation_result.warnings)
            summary['suggestions'].extend([issue.suggestion for issue in self.validation_result.issues if issue.suggestion])
        
        if self.optimization_result and self.optimization_result.suggestions:
            summary['suggestions'].extend([s.description for s in self.optimization_result.suggestions])
        
        return summary
    
    def split_content_from_string(self, content: str) -> Tuple[str, str]:
        """
        Split content from string instead of file.
        
        Args:
            content: Raw markdown content string
            
        Returns:
            Tuple of (slides_content, notes_content)
        """
        processed = self.process_directives(content)
        return processed["slides"], processed["notes"]
    
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
        
        # Copy referenced images to output directory
        self._copy_referenced_images(filepath, output_path)
        
        logger.info(f"Generated slides: {slides_path}")
        logger.info(f"Generated notes: {notes_path}")
        
        return str(slides_path), str(notes_path)
    
    def _copy_referenced_images(self, source_file: str, output_dir: Path) -> None:
        """
        Copy images referenced in the markdown file to the output directory.
        
        Args:
            source_file: Path to the source markdown file
            output_dir: Output directory to copy images to
        """
        import re
        import shutil
        
        source_path = Path(source_file)
        source_dir = source_path.parent
        
        # Read the original file to find image references
        try:
            content = source_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.warning(f"Could not read source file for image detection: {e}")
            return
        
        # Find image references in markdown: ![alt text](image.png)
        image_pattern = r'!\[.*?\]\(([^)]+)\)'
        image_matches = re.findall(image_pattern, content)
        
        for image_path in image_matches:
            # Skip URLs (http/https)
            if image_path.startswith(('http://', 'https://')):
                continue
                
            # Handle relative paths
            if not Path(image_path).is_absolute():
                source_image_path = source_dir / image_path
            else:
                source_image_path = Path(image_path)
            
            if source_image_path.exists():
                dest_image_path = output_dir / source_image_path.name
                try:
                    shutil.copy2(source_image_path, dest_image_path)
                    logger.info(f"Copied image: {source_image_path.name} -> {dest_image_path}")
                except Exception as e:
                    logger.warning(f"Failed to copy image {source_image_path}: {e}")
            else:
                logger.warning(f"Referenced image not found: {source_image_path}")
    
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
            # Check for slide separators
            if line.strip() == '---':
                # Save previous section if exists
                if current_section and current_section.content.strip():
                    sections.append(current_section)
                    slide_number += 1
                    current_section = None
                continue
            
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
                    if '$' in line:
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