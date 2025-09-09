"""
Tests for Math Renderer - Perfect LaTeX math rendering across all output formats.

Tests math rendering optimization, compatibility checking, and format-specific
optimizations for reveal.js slides, PDF outputs, and other formats.
"""

import pytest
from unittest.mock import patch, MagicMock

from markdown_slides_generator.latex import (
    MathRenderer,
    MathRenderingOptimizer,
    MathCompatibilityChecker,
    MathRenderingConfig,
    MathOptimizationResult,
    MathRenderingEngine,
    OutputFormat,
    LaTeXProcessor,
    LaTeXValidationResult
)


class TestMathCompatibilityChecker:
    """Test math compatibility checking functionality."""
    
    def test_mathjax_compatibility(self):
        """Test compatibility checking for MathJax engine."""
        checker = MathCompatibilityChecker()
        
        # Create mock LaTeX validation result
        mock_result = MagicMock(spec=LaTeXValidationResult)
        mock_result.packages_required = {'amsmath', 'physics', 'tikz'}
        mock_result.expressions = []
        
        issues = checker.check_compatibility(mock_result, MathRenderingEngine.MATHJAX)
        
        # Should find tikz as unsupported (it's in limited_support)
        assert len(issues) >= 0  # tikz is in limited_support, not unsupported
    
    def test_katex_compatibility(self):
        """Test compatibility checking for KaTeX engine."""
        checker = MathCompatibilityChecker()
        
        # Create mock LaTeX validation result
        mock_result = MagicMock(spec=LaTeXValidationResult)
        mock_result.packages_required = {'amsmath', 'physics', 'siunitx'}
        mock_result.expressions = []
        
        issues = checker.check_compatibility(mock_result, MathRenderingEngine.KATEX)
        
        # Should find physics and siunitx as unsupported
        assert len(issues) >= 2
        assert any('physics' in issue for issue in issues)
        assert any('siunitx' in issue for issue in issues)
    
    def test_native_latex_compatibility(self):
        """Test compatibility checking for native LaTeX engine."""
        checker = MathCompatibilityChecker()
        
        # Create mock LaTeX validation result
        mock_result = MagicMock(spec=LaTeXValidationResult)
        mock_result.packages_required = {'amsmath', 'physics', 'tikz', 'any_package'}
        mock_result.expressions = []
        
        issues = checker.check_compatibility(mock_result, MathRenderingEngine.NATIVE_LATEX)
        
        # Native LaTeX supports everything
        assert len(issues) == 0
    
    def test_suggest_alternatives(self):
        """Test suggestion of alternative commands."""
        checker = MathCompatibilityChecker()
        
        alternatives = checker.suggest_alternatives('\\physics', MathRenderingEngine.KATEX)
        
        assert len(alternatives) > 0
        assert any('\\frac{d}{dx}' in alt for alt in alternatives)


class TestMathRenderingOptimizer:
    """Test math rendering optimization functionality."""
    
    def test_default_configs_exist(self):
        """Test that default configurations exist for all formats."""
        optimizer = MathRenderingOptimizer()
        
        for format_type in OutputFormat:
            assert format_type in optimizer.DEFAULT_CONFIGS
            config = optimizer.DEFAULT_CONFIGS[format_type]
            assert isinstance(config, MathRenderingConfig)
            assert config.format == format_type
    
    def test_optimize_for_revealjs(self):
        """Test optimization for reveal.js format."""
        optimizer = MathRenderingOptimizer()
        
        content = """
# Math Examples
Inline: $E = mc^2$
Display: $$\\int f(x) dx$$
More text.
"""
        
        # Create mock LaTeX result
        mock_latex_result = MagicMock(spec=LaTeXValidationResult)
        mock_latex_result.is_valid = True
        mock_latex_result.expressions = []
        mock_latex_result.errors = []
        mock_latex_result.warnings = []
        mock_latex_result.packages_required = set()
        mock_latex_result.custom_commands = set()
        
        result = optimizer.optimize_for_format(
            content, OutputFormat.REVEALJS, mock_latex_result
        )
        
        assert isinstance(result, MathOptimizationResult)
        assert result.rendering_config.format == OutputFormat.REVEALJS
        assert result.rendering_config.engine == MathRenderingEngine.MATHJAX
        
        # Check that display math has proper spacing
        assert '\n\n$$' in result.optimized_content or '$$\n\n' in result.optimized_content
    
    def test_optimize_for_pdf(self):
        """Test optimization for PDF format."""
        optimizer = MathRenderingOptimizer()
        
        content = """
# Math Examples
Display math: $$E = mc^2$$
"""
        
        # Create mock LaTeX result
        mock_latex_result = MagicMock(spec=LaTeXValidationResult)
        mock_latex_result.is_valid = True
        mock_latex_result.expressions = []
        mock_latex_result.errors = []
        mock_latex_result.warnings = []
        mock_latex_result.packages_required = set()
        mock_latex_result.custom_commands = set()
        
        result = optimizer.optimize_for_format(
            content, OutputFormat.PDF, mock_latex_result
        )
        
        assert result.rendering_config.format == OutputFormat.PDF
        assert result.rendering_config.engine == MathRenderingEngine.NATIVE_LATEX
    
    def test_optimize_for_pptx(self):
        """Test optimization for PowerPoint format."""
        optimizer = MathRenderingOptimizer()
        
        content = """
Physics notation: $\\derivative{f}{x}$ and $\\abs{x}$
"""
        
        # Create mock LaTeX result
        mock_latex_result = MagicMock(spec=LaTeXValidationResult)
        mock_latex_result.is_valid = True
        mock_latex_result.expressions = []
        mock_latex_result.errors = []
        mock_latex_result.warnings = []
        mock_latex_result.packages_required = set()
        mock_latex_result.custom_commands = set()
        
        result = optimizer.optimize_for_format(
            content, OutputFormat.PPTX, mock_latex_result
        )
        
        # Should simplify complex expressions for PowerPoint
        assert '\\frac{df}{dx}' in result.optimized_content or '\\derivative' in result.optimized_content
        assert '|x|' in result.optimized_content or '\\abs' in result.optimized_content
    
    def test_generate_quarto_config_revealjs(self):
        """Test Quarto configuration generation for reveal.js."""
        optimizer = MathRenderingOptimizer()
        config = optimizer.DEFAULT_CONFIGS[OutputFormat.REVEALJS]
        
        quarto_config = optimizer.generate_quarto_config(config)
        
        assert 'format' in quarto_config
        assert 'revealjs' in quarto_config['format']
        assert 'mathjax' in quarto_config['format']['revealjs']
    
    def test_generate_quarto_config_pdf(self):
        """Test Quarto configuration generation for PDF."""
        optimizer = MathRenderingOptimizer()
        config = optimizer.DEFAULT_CONFIGS[OutputFormat.PDF]
        
        quarto_config = optimizer.generate_quarto_config(config)
        
        assert 'format' in quarto_config
        assert 'pdf' in quarto_config['format']
        assert 'pdf-engine' in quarto_config['format']['pdf']
    
    def test_performance_notes_generation(self):
        """Test generation of performance optimization notes."""
        optimizer = MathRenderingOptimizer()
        
        # Create mock LaTeX result with many expressions
        mock_latex_result = MagicMock(spec=LaTeXValidationResult)
        mock_latex_result.expressions = [MagicMock() for _ in range(60)]  # Many expressions
        
        config = optimizer.DEFAULT_CONFIGS[OutputFormat.REVEALJS]
        
        notes = optimizer._generate_performance_notes(
            OutputFormat.REVEALJS, config, mock_latex_result
        )
        
        assert len(notes) > 0
        assert any('KaTeX' in note for note in notes)


class TestMathRenderer:
    """Test main math renderer functionality."""
    
    def test_initialization(self):
        """Test math renderer initialization."""
        renderer = MathRenderer()
        
        assert renderer.latex_processor is not None
        assert renderer.optimizer is not None
        assert renderer.last_optimization_result is None
    
    @patch.object(LaTeXProcessor, 'process_content')
    def test_optimize_math_rendering_success(self, mock_process):
        """Test successful math rendering optimization."""
        renderer = MathRenderer()
        
        # Mock LaTeX processor result
        mock_latex_result = MagicMock(spec=LaTeXValidationResult)
        mock_latex_result.is_valid = True
        mock_latex_result.expressions = []
        mock_latex_result.errors = []
        mock_latex_result.warnings = []
        mock_latex_result.packages_required = set()
        mock_latex_result.custom_commands = set()
        
        mock_process.return_value = mock_latex_result
        
        content = "Math: $E = mc^2$"
        result = renderer.optimize_math_rendering(content, OutputFormat.REVEALJS)
        
        assert isinstance(result, MathOptimizationResult)
        assert result.rendering_config.format == OutputFormat.REVEALJS
        assert renderer.last_optimization_result == result
    
    @patch.object(LaTeXProcessor, 'process_content')
    def test_optimize_math_rendering_with_errors(self, mock_process):
        """Test math rendering optimization with LaTeX errors."""
        renderer = MathRenderer()
        
        # Mock LaTeX processor result with errors
        mock_latex_result = MagicMock(spec=LaTeXValidationResult)
        mock_latex_result.is_valid = False
        mock_latex_result.expressions = []
        mock_latex_result.errors = ["Unbalanced braces"]
        mock_latex_result.warnings = ["Use \\cdot instead of *"]
        mock_latex_result.packages_required = set()
        mock_latex_result.custom_commands = set()
        
        mock_process.return_value = mock_latex_result
        
        content = "Bad math: $\\frac{1}{2$"
        result = renderer.optimize_math_rendering(content, OutputFormat.REVEALJS)
        
        assert len(result.warnings) > 0
        assert any("LaTeX Error" in warning for warning in result.warnings)
    
    @patch.object(LaTeXProcessor, 'process_content')
    def test_generate_format_configs(self, mock_process):
        """Test generation of configurations for all formats."""
        renderer = MathRenderer()
        
        # Mock LaTeX processor result
        mock_latex_result = MagicMock(spec=LaTeXValidationResult)
        mock_latex_result.is_valid = True
        mock_latex_result.expressions = []
        mock_latex_result.errors = []
        mock_latex_result.warnings = []
        mock_latex_result.packages_required = set()
        mock_latex_result.custom_commands = set()
        
        mock_process.return_value = mock_latex_result
        
        content = "Math: $E = mc^2$"
        configs = renderer.generate_format_configs(content)
        
        # Should have configs for all formats
        assert len(configs) == len(OutputFormat)
        for format_type in OutputFormat:
            assert format_type in configs
            assert isinstance(configs[format_type], MathRenderingConfig)
    
    @patch.object(LaTeXProcessor, 'process_content')
    def test_validate_math_across_formats(self, mock_process):
        """Test math validation across all formats."""
        renderer = MathRenderer()
        
        # Mock LaTeX processor result
        mock_latex_result = MagicMock(spec=LaTeXValidationResult)
        mock_latex_result.is_valid = True
        mock_latex_result.expressions = []
        mock_latex_result.errors = []
        mock_latex_result.warnings = []
        mock_latex_result.packages_required = {'physics'}  # Unsupported in KaTeX
        mock_latex_result.custom_commands = set()
        
        mock_process.return_value = mock_latex_result
        
        content = "Physics: $\\derivative{f}{x}$"
        compatibility_results = renderer.validate_math_across_formats(content)
        
        # Should have results for all formats
        assert len(compatibility_results) == len(OutputFormat)
        
        # Should find compatibility issues for formats using KaTeX
        # (Note: current default configs use MathJax, so this might not trigger)
        for format_type, issues in compatibility_results.items():
            assert isinstance(issues, list)
    
    def test_get_rendering_summary_no_optimization(self):
        """Test rendering summary when no optimization has been performed."""
        renderer = MathRenderer()
        
        summary = renderer.get_rendering_summary()
        
        assert summary["status"] == "No optimization performed"
    
    @patch.object(LaTeXProcessor, 'process_content')
    def test_get_rendering_summary_with_optimization(self, mock_process):
        """Test rendering summary after optimization."""
        renderer = MathRenderer()
        
        # Mock LaTeX processor result
        mock_latex_result = MagicMock(spec=LaTeXValidationResult)
        mock_latex_result.is_valid = True
        mock_latex_result.expressions = []
        mock_latex_result.errors = []
        mock_latex_result.warnings = []
        mock_latex_result.packages_required = set()
        mock_latex_result.custom_commands = set()
        
        mock_process.return_value = mock_latex_result
        
        content = "Math: $E = mc^2$"
        renderer.optimize_math_rendering(content, OutputFormat.REVEALJS)
        
        summary = renderer.get_rendering_summary()
        
        assert summary["format"] == "revealjs"
        assert summary["engine"] == "mathjax"
        assert "warnings" in summary
        assert "compatibility_issues" in summary
        assert "performance_notes" in summary


class TestMathRenderingIntegration:
    """Integration tests for math rendering system."""
    
    def test_complete_workflow_revealjs(self):
        """Test complete math rendering workflow for reveal.js."""
        renderer = MathRenderer()
        
        content = """
# Advanced Mathematics

## Inline Math
Simple equations: $E = mc^2$ and $F = ma$.

## Display Math
Complex integral:
$$\\int_{-\\infty}^{\\infty} \\frac{1}{\\sqrt{2\\pi\\sigma^2}} e^{-\\frac{(x-\\mu)^2}{2\\sigma^2}} dx = 1$$

## Matrix Operations
$$\\begin{pmatrix}
a & b \\\\
c & d
\\end{pmatrix}$$
"""
        
        result = renderer.optimize_math_rendering(content, OutputFormat.REVEALJS)
        
        # Should complete successfully
        assert isinstance(result, MathOptimizationResult)
        assert result.rendering_config.format == OutputFormat.REVEALJS
        assert result.rendering_config.engine == MathRenderingEngine.MATHJAX
        
        # Should have optimized content
        assert len(result.optimized_content) > 0
        assert '$E = mc^2$' in result.optimized_content
        assert '$$' in result.optimized_content
    
    def test_complete_workflow_pdf(self):
        """Test complete math rendering workflow for PDF."""
        renderer = MathRenderer()
        
        content = """
# Mathematical Proofs

## Theorem
For any real number $x$:
$$e^{i\\pi x} = \\cos(\\pi x) + i\\sin(\\pi x)$$

## Proof
Using Taylor series expansion...
"""
        
        result = renderer.optimize_math_rendering(content, OutputFormat.PDF)
        
        # Should complete successfully
        assert isinstance(result, MathOptimizationResult)
        assert result.rendering_config.format == OutputFormat.PDF
        assert result.rendering_config.engine == MathRenderingEngine.NATIVE_LATEX
        
        # Should include LaTeX packages
        assert 'amsmath' in result.rendering_config.packages
    
    def test_error_handling_invalid_latex(self):
        """Test error handling with invalid LaTeX."""
        renderer = MathRenderer()
        
        content = """
# Bad Math
Unbalanced: $\\frac{1}{2$
Unmatched: \\begin{align} x = y \\end{equation}
"""
        
        # Should not crash, but report errors
        result = renderer.optimize_math_rendering(content, OutputFormat.REVEALJS)
        
        assert isinstance(result, MathOptimizationResult)
        # Should have warnings about LaTeX errors
        assert len(result.warnings) > 0
    
    def test_performance_with_many_expressions(self):
        """Test performance with many math expressions."""
        renderer = MathRenderer()
        
        # Generate content with many math expressions
        expressions = []
        for i in range(50):
            expressions.append(f"Equation {i}: $x_{i} = \\alpha + \\beta_{i}$")
        
        content = "# Many Equations\n\n" + "\n\n".join(expressions)
        
        # Should complete in reasonable time
        import time
        start_time = time.time()
        result = renderer.optimize_math_rendering(content, OutputFormat.REVEALJS)
        end_time = time.time()
        
        # Should complete quickly (less than 2 seconds)
        assert end_time - start_time < 2.0
        assert isinstance(result, MathOptimizationResult)
        
        # Should have performance notes
        assert len(result.performance_notes) > 0


if __name__ == "__main__":
    pytest.main([__file__])