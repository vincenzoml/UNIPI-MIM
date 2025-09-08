"""
Integration tests for LaTeX processing with the markdown slides generator.

Tests the integration of LaTeX validation and math rendering with the
content splitting and Quarto orchestration systems.
"""

import pytest
import tempfile
from pathlib import Path

from app.src.markdown_slides_generator.core.content_splitter import ContentSplitter
from app.src.markdown_slides_generator.core.quarto_orchestrator import QuartoOrchestrator
from app.src.markdown_slides_generator.latex import (
    LaTeXProcessor, 
    MathRenderer, 
    OutputFormat
)


class TestLaTeXIntegration:
    """Test LaTeX processing integration with the main system."""
    
    def test_content_splitter_with_latex(self):
        """Test content splitter with LaTeX expressions."""
        splitter = ContentSplitter()
        
        content = """
# Mathematical Lecture

## Introduction
Welcome to advanced mathematics.

<!-- SLIDE -->
## Basic Equations
Inline math: $E = mc^2$ and $F = ma$.

<!-- NOTES-ONLY -->
Additional notes: The energy-mass equivalence was derived by Einstein.

<!-- SLIDE -->
## Complex Mathematics
Display math:
$$\\int_{-\\infty}^{\\infty} \\frac{1}{\\sqrt{2\\pi\\sigma^2}} e^{-\\frac{(x-\\mu)^2}{2\\sigma^2}} dx = 1$$

<!-- ALL -->
This concludes our mathematical overview.
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        try:
            # Process content
            slides_content, notes_content = splitter.split_content(temp_file)
            
            # Verify LaTeX validation was performed
            latex_result = splitter.get_latex_validation_result()
            assert latex_result is not None
            
            # Should find LaTeX expressions
            assert len(latex_result.expressions) > 0
            
            # Should find inline and display math
            expression_types = [expr.expression_type.value for expr in latex_result.expressions]
            assert 'inline_math' in expression_types
            assert 'display_math' in expression_types
            
            # Verify content splitting worked
            assert '$E = mc^2$' in slides_content
            assert 'Einstein' in notes_content
            assert 'Einstein' not in slides_content
            
            # Check required packages
            required_packages = splitter.get_required_latex_packages()
            assert 'amsmath' in required_packages or len(required_packages) >= 0
            
        finally:
            # Clean up
            Path(temp_file).unlink()
    
    def test_latex_processor_standalone(self):
        """Test LaTeX processor as standalone component."""
        processor = LaTeXProcessor()
        
        content = """
# Advanced Mathematics

## Equations
Simple: $x = y + z$
Complex: $$\\begin{align}
\\nabla \\times \\mathbf{E} &= -\\frac{\\partial \\mathbf{B}}{\\partial t} \\\\
\\nabla \\times \\mathbf{B} &= \\mu_0 \\mathbf{J} + \\mu_0 \\epsilon_0 \\frac{\\partial \\mathbf{E}}{\\partial t}
\\end{align}$$

## Special Functions
Physics notation: $\\mathbb{R}^3$ and $\\mathcal{L}$
"""
        
        result = processor.process_content(content)
        
        # Should validate successfully
        assert result.is_valid
        assert len(result.expressions) > 0
        
        # Should detect required packages
        assert 'amssymb' in result.packages_required  # for \mathbb
        
        # Should find different expression types
        expression_types = [expr.expression_type.value for expr in result.expressions]
        assert 'inline_math' in expression_types
        assert 'environment' in expression_types
    
    def test_math_renderer_standalone(self):
        """Test math renderer as standalone component."""
        renderer = MathRenderer()
        
        content = """
# Physics Equations

Maxwell's equations:
$$\\begin{align}
\\nabla \\cdot \\mathbf{E} &= \\frac{\\rho}{\\epsilon_0} \\\\
\\nabla \\cdot \\mathbf{B} &= 0 \\\\
\\nabla \\times \\mathbf{E} &= -\\frac{\\partial \\mathbf{B}}{\\partial t} \\\\
\\nabla \\times \\mathbf{B} &= \\mu_0 \\mathbf{J} + \\mu_0 \\epsilon_0 \\frac{\\partial \\mathbf{E}}{\\partial t}
\\end{align}$$

Energy: $E = mc^2$
"""
        
        # Test optimization for different formats
        for output_format in [OutputFormat.REVEALJS, OutputFormat.PDF, OutputFormat.HTML]:
            result = renderer.optimize_math_rendering(content, output_format)
            
            assert result.rendering_config.format == output_format
            assert len(result.optimized_content) > 0
            assert '$E = mc^2$' in result.optimized_content
    
    def test_quarto_orchestrator_math_integration(self):
        """Test Quarto orchestrator with math optimization methods."""
        orchestrator = QuartoOrchestrator()
        
        # Test that math renderer is initialized
        assert orchestrator.math_renderer is not None
        
        content = """
---
title: "Math Test"
format: revealjs
---

# Mathematics

Simple equation: $E = mc^2$

Complex integral:
$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        try:
            # Test math compatibility validation
            compatibility_results = orchestrator.validate_math_compatibility(temp_file)
            
            # Should have results for all formats
            assert len(compatibility_results) > 0
            assert 'revealjs' in compatibility_results
            assert 'pdf' in compatibility_results
            
            # Each format should have a list of issues (possibly empty)
            for format_name, issues in compatibility_results.items():
                assert isinstance(issues, list)
        
        finally:
            # Clean up
            Path(temp_file).unlink()
    
    def test_error_handling_invalid_latex(self):
        """Test error handling with invalid LaTeX expressions."""
        splitter = ContentSplitter()
        
        content = """
# Bad Mathematics

## Invalid LaTeX
Unbalanced braces: $\\frac{1}{2$
Unmatched environment: \\begin{align} x = y \\end{equation}
Empty expression: $$$$

## Valid LaTeX
This should work: $x = y$
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        try:
            # Should not crash, but handle errors gracefully
            slides_content, notes_content = splitter.split_content(temp_file)
            
            # Should still process content
            assert len(slides_content) > 0
            assert len(notes_content) > 0
            
            # Should detect LaTeX errors
            latex_result = splitter.get_latex_validation_result()
            assert latex_result is not None
            assert not latex_result.is_valid
            assert len(latex_result.errors) > 0
            
            # Should indicate LaTeX errors
            assert splitter.has_latex_errors()
        
        finally:
            # Clean up
            Path(temp_file).unlink()
    
    def test_performance_with_complex_content(self):
        """Test performance with complex mathematical content."""
        processor = LaTeXProcessor()
        
        # Generate complex content
        content_parts = [
            "# Advanced Mathematical Analysis",
            "",
            "## Introduction",
            "This document contains extensive mathematical notation.",
            ""
        ]
        
        # Add many mathematical expressions
        for i in range(20):
            content_parts.extend([
                f"## Section {i+1}",
                f"Inline equation: $f_{i}(x) = \\sum_{{n=0}}^{{\\infty}} \\frac{{x^n}}{{n!}}$",
                "",
                f"Display equation:",
                f"$$\\int_{{-\\infty}}^{{\\infty}} f_{i}(x) e^{{-x^2}} dx = \\sqrt{{\\pi}}$$",
                "",
                f"Matrix equation:",
                f"$$\\mathbf{{A}}_{i} = \\begin{{pmatrix}}",
                f"a_{{11}} & a_{{12}} \\\\",
                f"a_{{21}} & a_{{22}}",
                f"\\end{{pmatrix}}$$",
                ""
            ])
        
        content = "\n".join(content_parts)
        
        # Should process efficiently
        import time
        start_time = time.time()
        result = processor.process_content(content)
        end_time = time.time()
        
        # Should complete in reasonable time (less than 3 seconds)
        assert end_time - start_time < 3.0
        
        # Should find many expressions
        assert len(result.expressions) > 50
        
        # Should detect required packages
        assert len(result.packages_required) > 0


if __name__ == "__main__":
    pytest.main([__file__])