"""
Math Renderer - Ensures perfect LaTeX math rendering across all output formats.

Provides format-specific optimizations for LaTeX math rendering in reveal.js slides,
PDF outputs, and other formats. Integrates with Quarto's built-in math rendering
while adding validation and optimization layers.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum

from ..utils.logger import get_logger
from ..utils.exceptions import handle_exception, OutputError
from .latex_processor import LaTeXProcessor, LaTeXValidationResult

logger = get_logger(__name__)


class MathRenderingEngine(Enum):
    """Math rendering engines supported by different output formats."""
    MATHJAX = "mathjax"
    KATEX = "katex"
    NATIVE_LATEX = "native"
    WEBTEX = "webtex"


class OutputFormat(Enum):
    """Output formats with different math rendering requirements."""
    REVEALJS = "revealjs"
    HTML = "html"
    PDF = "pdf"
    BEAMER = "beamer"
    PPTX = "pptx"


@dataclass
class MathRenderingConfig:
    """Configuration for math rendering in specific output format."""
    format: OutputFormat
    engine: MathRenderingEngine
    engine_options: Dict[str, Any]
    packages: List[str]
    macros: Dict[str, str]
    delimiters: Dict[str, List[str]]
    
    def __post_init__(self):
        if not hasattr(self, 'engine_options'):
            self.engine_options = {}
        if not hasattr(self, 'packages'):
            self.packages = []
        if not hasattr(self, 'macros'):
            self.macros = {}
        if not hasattr(self, 'delimiters'):
            self.delimiters = {}


@dataclass
class MathOptimizationResult:
    """Result of math rendering optimization."""
    optimized_content: str
    rendering_config: MathRenderingConfig
    warnings: List[str]
    performance_notes: List[str]
    compatibility_issues: List[str]
    
    def __post_init__(self):
        if not hasattr(self, 'warnings'):
            self.warnings = []
        if not hasattr(self, 'performance_notes'):
            self.performance_notes = []
        if not hasattr(self, 'compatibility_issues'):
            self.compatibility_issues = []


class MathCompatibilityChecker:
    """
    Checks LaTeX math expressions for compatibility across different rendering engines.
    
    Identifies potential issues with specific LaTeX commands or environments
    that may not render correctly in certain output formats.
    """
    
    # Commands that may have compatibility issues
    COMPATIBILITY_MATRIX = {
        MathRenderingEngine.MATHJAX: {
            'supported_packages': {
                'amsmath', 'amssymb', 'amsthm', 'mathtools', 'physics',
                'siunitx', 'cancel', 'color', 'bbox', 'enclose'
            },
            'unsupported_commands': {
                '\\includegraphics', '\\input', '\\include', '\\newcommand',
                '\\renewcommand', '\\def', '\\let'
            },
            'limited_support': {
                '\\tikz', '\\pgfplots', '\\chemfig', '\\feynman'
            }
        },
        MathRenderingEngine.KATEX: {
            'supported_packages': {
                'amsmath', 'amssymb', 'mathtools', 'cancel', 'color'
            },
            'unsupported_commands': {
                '\\includegraphics', '\\input', '\\include', '\\newcommand',
                '\\renewcommand', '\\def', '\\let', '\\physics', '\\siunitx'
            },
            'limited_support': {
                '\\substack', '\\genfrac', '\\cfrac'
            }
        },
        MathRenderingEngine.NATIVE_LATEX: {
            'supported_packages': 'all',  # Native LaTeX supports everything
            'unsupported_commands': set(),
            'limited_support': set()
        }
    }
    
    def __init__(self):
        self.compatibility_issues: List[str] = []
    
    def check_compatibility(
        self, 
        latex_result: LaTeXValidationResult, 
        target_engine: MathRenderingEngine
    ) -> List[str]:
        """
        Check LaTeX expressions for compatibility with target rendering engine.
        
        Args:
            latex_result: LaTeX validation result from LaTeXProcessor
            target_engine: Target math rendering engine
            
        Returns:
            List of compatibility issue descriptions
        """
        self.compatibility_issues = []
        
        if target_engine not in self.COMPATIBILITY_MATRIX:
            return []
        
        engine_info = self.COMPATIBILITY_MATRIX[target_engine]
        
        # Check package compatibility
        if engine_info['supported_packages'] != 'all':
            unsupported_packages = (
                latex_result.packages_required - 
                engine_info['supported_packages']
            )
            for package in unsupported_packages:
                self.compatibility_issues.append(
                    f"Package '{package}' is not supported by {target_engine.value}"
                )
        
        # Check command compatibility
        for expr in latex_result.expressions:
            content = expr.content
            
            # Check for unsupported commands
            for unsupported_cmd in engine_info['unsupported_commands']:
                if unsupported_cmd in content:
                    self.compatibility_issues.append(
                        f"Line {expr.line_number}: Command '{unsupported_cmd}' "
                        f"is not supported by {target_engine.value}"
                    )
            
            # Check for commands with limited support
            for limited_cmd in engine_info['limited_support']:
                if limited_cmd in content:
                    self.compatibility_issues.append(
                        f"Line {expr.line_number}: Command '{limited_cmd}' "
                        f"has limited support in {target_engine.value}"
                    )
        
        return self.compatibility_issues
    
    def suggest_alternatives(self, unsupported_command: str, target_engine: MathRenderingEngine) -> List[str]:
        """Suggest alternative commands for unsupported LaTeX commands."""
        alternatives = {
            '\\physics': {
                MathRenderingEngine.KATEX: [
                    'Use \\frac{d}{dx} instead of \\derivative{}{x}',
                    'Use \\partial instead of \\partialderivative',
                    'Use |x| instead of \\abs{x}'
                ]
            },
            '\\siunitx': {
                MathRenderingEngine.KATEX: [
                    'Use \\text{unit} for units instead of \\si{unit}',
                    'Use regular numbers instead of \\num{}'
                ]
            }
        }
        
        return alternatives.get(unsupported_command, {}).get(target_engine, [])


class MathRenderingOptimizer:
    """
    Optimizes LaTeX math expressions for specific output formats and rendering engines.
    
    Provides format-specific optimizations to ensure the best possible math rendering
    quality and performance across different output formats.
    """
    
    # Default configurations for different output formats
    DEFAULT_CONFIGS = {
        OutputFormat.REVEALJS: MathRenderingConfig(
            format=OutputFormat.REVEALJS,
            engine=MathRenderingEngine.MATHJAX,
            engine_options={
                'tex': {
                    'inlineMath': [['$', '$'], ['\\(', '\\)']],
                    'displayMath': [['$$', '$$'], ['\\[', '\\]']],
                    'processEscapes': True,
                    'processEnvironments': True,
                    'tags': 'ams'
                },
                'options': {
                    'skipHtmlTags': ['script', 'noscript', 'style', 'textarea', 'pre'],
                    'ignoreHtmlClass': 'tex2jax_ignore',
                    'processHtmlClass': 'tex2jax_process'
                },
                'loader': {
                    'load': ['[tex]/ams', '[tex]/physics', '[tex]/color', '[tex]/cancel']
                }
            },
            packages=['amsmath', 'amssymb', 'physics', 'color', 'cancel'],
            macros={},
            delimiters={
                'inline': ['$', '$'],
                'display': ['$$', '$$']
            }
        ),
        
        OutputFormat.HTML: MathRenderingConfig(
            format=OutputFormat.HTML,
            engine=MathRenderingEngine.MATHJAX,
            engine_options={
                'tex': {
                    'inlineMath': [['$', '$'], ['\\(', '\\)']],
                    'displayMath': [['$$', '$$'], ['\\[', '\\]']],
                    'processEscapes': True,
                    'processEnvironments': True,
                    'tags': 'ams'
                },
                'chtml': {
                    'fontURL': 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/output/chtml/fonts/woff-v2'
                }
            },
            packages=['amsmath', 'amssymb', 'amsthm', 'physics'],
            macros={},
            delimiters={
                'inline': ['$', '$'],
                'display': ['$$', '$$']
            }
        ),
        
        OutputFormat.PDF: MathRenderingConfig(
            format=OutputFormat.PDF,
            engine=MathRenderingEngine.NATIVE_LATEX,
            engine_options={
                'pdf-engine': 'xelatex',
                'pdf-engine-opts': ['-shell-escape'],
                'include-in-header': []
            },
            packages=['amsmath', 'amssymb', 'amsthm', 'mathtools', 'physics', 'siunitx'],
            macros={},
            delimiters={
                'inline': ['$', '$'],
                'display': ['$$', '$$']
            }
        ),
        
        OutputFormat.BEAMER: MathRenderingConfig(
            format=OutputFormat.BEAMER,
            engine=MathRenderingEngine.NATIVE_LATEX,
            engine_options={
                'pdf-engine': 'xelatex',
                'pdf-engine-opts': ['-shell-escape']
            },
            packages=['amsmath', 'amssymb', 'amsthm', 'mathtools', 'physics'],
            macros={},
            delimiters={
                'inline': ['$', '$'],
                'display': ['$$', '$$']
            }
        ),
        
        OutputFormat.PPTX: MathRenderingConfig(
            format=OutputFormat.PPTX,
            engine=MathRenderingEngine.NATIVE_LATEX,  # Converted to Office Math
            engine_options={
                'extract-media': './media'
            },
            packages=['amsmath', 'amssymb'],  # Limited support
            macros={},
            delimiters={
                'inline': ['$', '$'],
                'display': ['$$', '$$']
            }
        )
    }
    
    def __init__(self):
        self.compatibility_checker = MathCompatibilityChecker()
    
    def optimize_for_format(
        self, 
        content: str, 
        target_format: OutputFormat,
        latex_result: Optional[LaTeXValidationResult] = None,
        custom_config: Optional[MathRenderingConfig] = None
    ) -> MathOptimizationResult:
        """
        Optimize math rendering for specific output format.
        
        Args:
            content: Markdown content with LaTeX math
            target_format: Target output format
            latex_result: Optional pre-computed LaTeX validation result
            custom_config: Optional custom rendering configuration
            
        Returns:
            MathOptimizationResult with optimized content and configuration
        """
        logger.info(f"Optimizing math rendering for {target_format.value} format")
        
        # Get or create LaTeX validation result
        if latex_result is None:
            latex_processor = LaTeXProcessor()
            latex_result = latex_processor.process_content(content)
        
        # Get rendering configuration
        config = custom_config or self.DEFAULT_CONFIGS.get(
            target_format, 
            self.DEFAULT_CONFIGS[OutputFormat.HTML]
        )
        
        # Check compatibility
        compatibility_issues = self.compatibility_checker.check_compatibility(
            latex_result, config.engine
        )
        
        # Optimize content based on format
        optimized_content = self._optimize_content_for_format(
            content, target_format, config, latex_result
        )
        
        # Generate performance notes
        performance_notes = self._generate_performance_notes(
            target_format, config, latex_result
        )
        
        # Generate warnings
        warnings = []
        if not latex_result.is_valid:
            warnings.extend([f"LaTeX Error: {error}" for error in latex_result.errors])
        if latex_result.warnings:
            warnings.extend([f"LaTeX Warning: {warning}" for warning in latex_result.warnings])
        
        return MathOptimizationResult(
            optimized_content=optimized_content,
            rendering_config=config,
            warnings=warnings,
            performance_notes=performance_notes,
            compatibility_issues=compatibility_issues
        )
    
    def _optimize_content_for_format(
        self, 
        content: str, 
        target_format: OutputFormat,
        config: MathRenderingConfig,
        latex_result: LaTeXValidationResult
    ) -> str:
        """Optimize content for specific format."""
        optimized_content = content
        
        if target_format == OutputFormat.REVEALJS:
            # Optimize for reveal.js slides
            optimized_content = self._optimize_for_revealjs(optimized_content, latex_result)
        
        elif target_format == OutputFormat.PDF:
            # Optimize for PDF output
            optimized_content = self._optimize_for_pdf(optimized_content, latex_result)
        
        elif target_format == OutputFormat.PPTX:
            # Optimize for PowerPoint
            optimized_content = self._optimize_for_pptx(optimized_content, latex_result)
        
        return optimized_content
    
    def _optimize_for_revealjs(self, content: str, latex_result: LaTeXValidationResult) -> str:
        """Optimize math expressions for reveal.js slides."""
        # Ensure proper spacing around display math
        content = re.sub(r'([^\n])\$\$', r'\1\n\n$$', content)
        content = re.sub(r'\$\$([^\n])', r'$$\n\n\1', content)
        
        # Add fragment classes for complex equations (for step-by-step reveals)
        content = self._add_fragment_classes_to_complex_math(content, latex_result)
        
        return content
    
    def _optimize_for_pdf(self, content: str, latex_result: LaTeXValidationResult) -> str:
        """Optimize math expressions for PDF output."""
        # Ensure proper line breaks around display math
        content = re.sub(r'([^\n])\$\$', r'\1\n\n$$', content)
        content = re.sub(r'\$\$([^\n])', r'$$\n\n\1', content)
        
        # Add equation numbering where appropriate
        content = self._add_equation_numbering(content, latex_result)
        
        return content
    
    def _optimize_for_pptx(self, content: str, latex_result: LaTeXValidationResult) -> str:
        """Optimize math expressions for PowerPoint output."""
        # PowerPoint has limited LaTeX support, so simplify complex expressions
        content = self._simplify_complex_expressions(content, latex_result)
        
        return content
    
    def _add_fragment_classes_to_complex_math(
        self, 
        content: str, 
        latex_result: LaTeXValidationResult
    ) -> str:
        """Add reveal.js fragment classes to complex math expressions."""
        # This would add fragment classes for step-by-step reveals
        # For now, return content unchanged
        return content
    
    def _add_equation_numbering(self, content: str, latex_result: LaTeXValidationResult) -> str:
        """Add equation numbering for PDF output."""
        # Convert display math to equation environments where appropriate
        lines = content.split('\n')
        in_display_math = False
        result_lines = []
        
        for line in lines:
            if line.strip() == '$$' and not in_display_math:
                # Start of display math
                in_display_math = True
                result_lines.append('\\begin{equation}')
            elif line.strip() == '$$' and in_display_math:
                # End of display math
                in_display_math = False
                result_lines.append('\\end{equation}')
            else:
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _simplify_complex_expressions(
        self, 
        content: str, 
        latex_result: LaTeXValidationResult
    ) -> str:
        """Simplify complex LaTeX expressions for PowerPoint compatibility."""
        # Replace complex commands with simpler alternatives
        replacements = {
            r'\\derivative\{([^}]+)\}\{([^}]+)\}': r'\\frac{d\1}{d\2}',
            r'\\partialderivative\{([^}]+)\}\{([^}]+)\}': r'\\frac{\\partial \1}{\\partial \2}',
            r'\\abs\{([^}]+)\}': r'|\1|',
            r'\\norm\{([^}]+)\}': r'\\|\1\\|'
        }
        
        for pattern, replacement in replacements.items():
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _generate_performance_notes(
        self, 
        target_format: OutputFormat,
        config: MathRenderingConfig,
        latex_result: LaTeXValidationResult
    ) -> List[str]:
        """Generate performance optimization notes."""
        notes = []
        
        # Count math expressions
        total_expressions = len(latex_result.expressions)
        
        if total_expressions > 50:
            if config.engine == MathRenderingEngine.MATHJAX:
                notes.append(
                    f"Consider using KaTeX for better performance with {total_expressions} math expressions"
                )
            elif config.engine == MathRenderingEngine.KATEX:
                notes.append(
                    f"KaTeX should provide good performance for {total_expressions} math expressions"
                )
        
        # Check for complex environments
        complex_envs = [
            expr for expr in latex_result.expressions 
            if 'align' in expr.content or 'matrix' in expr.content
        ]
        
        if len(complex_envs) > 10:
            notes.append(
                f"Found {len(complex_envs)} complex math environments - "
                "consider breaking into smaller chunks for better rendering performance"
            )
        
        return notes
    
    def generate_quarto_config(self, config: MathRenderingConfig) -> Dict[str, Any]:
        """Generate Quarto YAML configuration for math rendering."""
        quarto_config = {}
        
        if config.format == OutputFormat.REVEALJS:
            quarto_config = {
                'format': {
                    'revealjs': {
                        'mathjax': config.engine_options,
                        'include-in-header': self._generate_mathjax_config(config)
                    }
                }
            }
        
        elif config.format == OutputFormat.HTML:
            quarto_config = {
                'format': {
                    'html': {
                        'mathjax': config.engine_options,
                        'include-in-header': self._generate_mathjax_config(config)
                    }
                }
            }
        
        elif config.format in [OutputFormat.PDF, OutputFormat.BEAMER]:
            quarto_config = {
                'format': {
                    config.format.value: {
                        'pdf-engine': config.engine_options.get('pdf-engine', 'xelatex'),
                        'pdf-engine-opts': config.engine_options.get('pdf-engine-opts', []),
                        'include-in-header': self._generate_latex_header(config)
                    }
                }
            }
        
        return quarto_config
    
    def _generate_mathjax_config(self, config: MathRenderingConfig) -> List[str]:
        """Generate MathJax configuration for HTML/reveal.js output."""
        mathjax_config = f"""
<script>
window.MathJax = {{
  tex: {{
    inlineMath: {json.dumps(config.engine_options.get('tex', {}).get('inlineMath', [['$', '$']]))},
    displayMath: {json.dumps(config.engine_options.get('tex', {}).get('displayMath', [['$$', '$$']]))},
    processEscapes: {json.dumps(config.engine_options.get('tex', {}).get('processEscapes', True))},
    processEnvironments: {json.dumps(config.engine_options.get('tex', {}).get('processEnvironments', True))},
    packages: {json.dumps(config.packages)},
    macros: {json.dumps(config.macros)}
  }},
  options: {{
    skipHtmlTags: {json.dumps(config.engine_options.get('options', {}).get('skipHtmlTags', []))},
    ignoreHtmlClass: "{config.engine_options.get('options', {}).get('ignoreHtmlClass', 'tex2jax_ignore')}",
    processHtmlClass: "{config.engine_options.get('options', {}).get('processHtmlClass', 'tex2jax_process')}"
  }}
}};
</script>
"""
        return [mathjax_config]
    
    def _generate_latex_header(self, config: MathRenderingConfig) -> List[str]:
        """Generate LaTeX header for PDF/Beamer output."""
        header_lines = []
        
        # Add package imports
        for package in config.packages:
            header_lines.append(f"\\usepackage{{{package}}}")
        
        # Add custom macros
        for macro_name, macro_def in config.macros.items():
            header_lines.append(f"\\newcommand{{\\{macro_name}}}{{{macro_def}}}")
        
        return header_lines


class MathRenderer:
    """
    Main math rendering system that ensures perfect LaTeX math rendering across all output formats.
    
    Integrates LaTeX validation, compatibility checking, and format-specific optimizations
    to provide the best possible math rendering experience in all supported output formats.
    """
    
    def __init__(self):
        self.latex_processor = LaTeXProcessor()
        self.optimizer = MathRenderingOptimizer()
        self.last_optimization_result: Optional[MathOptimizationResult] = None
    
    @handle_exception
    def optimize_math_rendering(
        self, 
        content: str, 
        target_format: OutputFormat,
        custom_config: Optional[MathRenderingConfig] = None
    ) -> MathOptimizationResult:
        """
        Optimize math rendering for specific output format with comprehensive validation.
        
        Args:
            content: Markdown content with LaTeX math expressions
            target_format: Target output format
            custom_config: Optional custom rendering configuration
            
        Returns:
            MathOptimizationResult with optimized content and configuration
            
        Raises:
            OutputError: If math rendering optimization fails
        """
        logger.info(f"Optimizing math rendering for {target_format.value}")
        
        try:
            # First, validate LaTeX expressions
            latex_result = self.latex_processor.process_content(content)
            
            # Then optimize for target format
            optimization_result = self.optimizer.optimize_for_format(
                content, target_format, latex_result, custom_config
            )
            
            self.last_optimization_result = optimization_result
            
            # Log results
            if optimization_result.warnings:
                logger.warning(f"Math rendering warnings: {len(optimization_result.warnings)}")
                for warning in optimization_result.warnings:
                    logger.warning(warning)
            
            if optimization_result.compatibility_issues:
                logger.warning(f"Compatibility issues: {len(optimization_result.compatibility_issues)}")
                for issue in optimization_result.compatibility_issues:
                    logger.warning(issue)
            
            if optimization_result.performance_notes:
                logger.info("Performance optimization notes:")
                for note in optimization_result.performance_notes:
                    logger.info(f"  - {note}")
            
            logger.info(f"Math rendering optimization completed for {target_format.value}")
            return optimization_result
            
        except Exception as e:
            raise OutputError(f"Failed to optimize math rendering for {target_format.value}: {e}")
    
    def generate_format_configs(self, content: str) -> Dict[OutputFormat, MathRenderingConfig]:
        """
        Generate optimized math rendering configurations for all supported formats.
        
        Args:
            content: Markdown content with LaTeX math expressions
            
        Returns:
            Dictionary mapping output formats to their optimized configurations
        """
        logger.info("Generating math rendering configurations for all formats")
        
        # Validate LaTeX once
        latex_result = self.latex_processor.process_content(content)
        
        configs = {}
        for format_type in OutputFormat:
            try:
                optimization_result = self.optimizer.optimize_for_format(
                    content, format_type, latex_result
                )
                configs[format_type] = optimization_result.rendering_config
            except Exception as e:
                logger.error(f"Failed to generate config for {format_type.value}: {e}")
                # Use default config as fallback
                configs[format_type] = self.optimizer.DEFAULT_CONFIGS.get(
                    format_type, 
                    self.optimizer.DEFAULT_CONFIGS[OutputFormat.HTML]
                )
        
        return configs
    
    def validate_math_across_formats(self, content: str) -> Dict[OutputFormat, List[str]]:
        """
        Validate math expressions for compatibility across all output formats.
        
        Args:
            content: Markdown content with LaTeX math expressions
            
        Returns:
            Dictionary mapping output formats to lists of compatibility issues
        """
        logger.info("Validating math compatibility across all formats")
        
        latex_result = self.latex_processor.process_content(content)
        compatibility_results = {}
        
        for format_type in OutputFormat:
            config = self.optimizer.DEFAULT_CONFIGS.get(
                format_type, 
                self.optimizer.DEFAULT_CONFIGS[OutputFormat.HTML]
            )
            
            issues = self.optimizer.compatibility_checker.check_compatibility(
                latex_result, config.engine
            )
            compatibility_results[format_type] = issues
        
        return compatibility_results
    
    def get_rendering_summary(self) -> Dict[str, Any]:
        """Get a summary of the last math rendering optimization."""
        if not self.last_optimization_result:
            return {"status": "No optimization performed"}
        
        result = self.last_optimization_result
        
        return {
            "format": result.rendering_config.format.value,
            "engine": result.rendering_config.engine.value,
            "warnings": len(result.warnings),
            "compatibility_issues": len(result.compatibility_issues),
            "performance_notes": len(result.performance_notes),
            "packages_required": result.rendering_config.packages,
            "has_custom_macros": bool(result.rendering_config.macros)
        }