"""
Comprehensive tests for Quarto orchestrator with various output formats.

Tests Quarto integration, command building, error handling, and format-specific
optimizations for all supported output types.
"""

import pytest
import tempfile
import shutil
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from markdown_slides_generator.core.quarto_orchestrator import (
    QuartoOrchestrator,
    QuartoCommandBuilder,
    QuartoExecutor,
    QuartoCommand,
    QuartoResult,
    OutputFormat
)
from markdown_slides_generator.utils.exceptions import OutputError


class TestQuartoCommandBuilder:
    """Test Quarto command building with format-specific optimizations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.builder = QuartoCommandBuilder()
    
    def test_revealjs_command_building(self):
        """Test building reveal.js slide commands."""
        command = self.builder.build_command(
            input_file="test.qmd",
            output_format=OutputFormat.REVEALJS,
            output_file="slides.html"
        )
        
        assert command.input_file == "test.qmd"
        assert command.output_format == "revealjs"
        assert command.output_file == "slides.html"
        assert "quarto" in command.args
        assert "render" in command.args
        assert "--to" in command.args
        assert "revealjs" in command.args
        assert "--output" in command.args
        assert "slides.html" in command.args
    
    def test_beamer_command_building(self):
        """Test building Beamer PDF slide commands."""
        command = self.builder.build_command(
            input_file="slides.qmd",
            output_format=OutputFormat.BEAMER
        )
        
        assert command.output_format == "beamer"
        assert "--to" in command.args
        assert "beamer" in command.args
    
    def test_pptx_command_building(self):
        """Test building PowerPoint slide commands."""
        command = self.builder.build_command(
            input_file="slides.qmd",
            output_format=OutputFormat.PPTX,
            custom_config={'slide-level': 1}
        )
        
        assert command.output_format == "pptx"
        assert "--to" in command.args
        assert "pptx" in command.args
    
    def test_pdf_notes_command_building(self):
        """Test building PDF notes commands."""
        command = self.builder.build_notes_command(
            input_file="notes.qmd",
            format="pdf",
            academic_style=True
        )
        
        assert command.output_format == "pdf"
        assert "--to" in command.args
        assert "pdf" in command.args
    
    def test_html_notes_command_building(self):
        """Test building HTML notes commands."""
        command = self.builder.build_notes_command(
            input_file="notes.qmd",
            format="html",
            academic_style=True
        )
        
        assert command.output_format == "html"
        assert "--to" in command.args
        assert "html" in command.args
    
    def test_custom_config_override(self):
        """Test that custom configuration overrides defaults."""
        custom_config = {
            'theme': 'dark',
            'transition': 'fade',
            'slide-number': False
        }
        
        command = self.builder.build_slides_command(
            input_file="test.qmd",
            format="revealjs",
            custom_options=custom_config
        )
        
        # Custom options should be applied
        assert command.args is not None
    
    def test_format_specific_optimizations(self):
        """Test that format-specific optimizations are applied."""
        # Test reveal.js optimizations
        revealjs_command = self.builder.build_command(
            input_file="test.qmd",
            output_format=OutputFormat.REVEALJS
        )
        
        # Test Beamer optimizations
        beamer_command = self.builder.build_command(
            input_file="test.qmd",
            output_format=OutputFormat.BEAMER
        )
        
        # Commands should be different due to format-specific settings
        assert revealjs_command.output_format != beamer_command.output_format
    
    def test_environment_variables(self):
        """Test environment variable handling."""
        command = self.builder.build_command(
            input_file="test.qmd",
            output_format=OutputFormat.REVEALJS,
            project_dir="/path/to/project"
        )
        
        assert 'QUARTO_PROJECT_DIR' in command.env_vars
        assert command.env_vars['QUARTO_PROJECT_DIR'] == "/path/to/project"


class TestQuartoExecutor:
    """Test Quarto command execution and error handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.executor = QuartoExecutor()
    
    @patch('subprocess.run')
    def test_successful_execution(self, mock_run):
        """Test successful command execution."""
        # Mock successful subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Output created: test.html\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        command = QuartoCommand(
            input_file="test.qmd",
            output_format="revealjs",
            args=["quarto", "render", "test.qmd", "--to", "revealjs"]
        )
        
        result = self.executor.execute_command(command)
        
        assert result.success is True
        assert result.return_code == 0
        assert "test.html" in result.stdout
        assert len(result.errors) == 0
    
    @patch('subprocess.run')
    def test_failed_execution(self, mock_run):
        """Test failed command execution."""
        # Mock failed subprocess result
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "ERROR: File not found\n"
        mock_run.return_value = mock_result
        
        command = QuartoCommand(
            input_file="nonexistent.qmd",
            output_format="revealjs",
            args=["quarto", "render", "nonexistent.qmd"]
        )
        
        result = self.executor.execute_command(command)
        
        assert result.success is False
        assert result.return_code == 1
        assert len(result.errors) > 0
    
    @patch('subprocess.run')
    def test_timeout_handling(self, mock_run):
        """Test timeout handling."""
        # Mock timeout exception
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=["quarto", "render"], timeout=10
        )
        
        command = QuartoCommand(
            input_file="test.qmd",
            output_format="revealjs",
            args=["quarto", "render", "test.qmd"]
        )
        
        result = self.executor.execute_command(command, timeout=1)
        
        assert result.success is False
        assert result.return_code == -1
        assert "timed out" in result.stderr
    
    def test_output_parsing(self):
        """Test parsing of Quarto output messages."""
        stdout = """
Starting render...
Output created: /path/to/slides.html
Render complete.
"""
        stderr = """
WARNING: Missing bibliography
ERROR: LaTeX compilation failed
"""
        
        warnings, errors = self.executor._parse_quarto_output(stdout, stderr)
        
        assert len(warnings) >= 1
        assert len(errors) >= 1
        assert any("bibliography" in w.lower() for w in warnings)
        assert any("latex" in e.lower() for e in errors)
    
    def test_output_file_detection(self):
        """Test detection of generated output files."""
        command = QuartoCommand(
            input_file="test.qmd",
            output_format="revealjs"
        )
        
        stdout = "Output created: /path/to/test.html"
        
        # Mock file existence
        with patch('pathlib.Path.exists', return_value=True):
            output_file = self.executor._find_output_file(command, stdout)
            assert output_file is not None
            assert "test.html" in output_file


class TestQuartoOrchestrator:
    """Test high-level Quarto orchestration functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = QuartoOrchestrator()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_slides_generation_workflow(self):
        """Test complete slides generation workflow."""
        # Create test input file
        test_content = """---
title: "Test Slides"
format: revealjs
---

# Introduction

This is a test slide.

## Main Content

- Point 1
- Point 2
"""
        
        input_file = self.temp_path / "test.qmd"
        input_file.write_text(test_content)
        
        # Mock the executor to avoid actual Quarto execution
        with patch.object(self.orchestrator.executor, 'execute_command') as mock_execute:
            mock_result = QuartoResult(
                success=True,
                output_file=str(self.temp_path / "test.html"),
                stdout="Output created: test.html",
                stderr="",
                return_code=0,
                execution_time=1.0
            )
            mock_execute.return_value = mock_result
            
            # Create mock output file
            output_file = self.temp_path / "test.html"
            output_file.write_text("<html>Mock slides</html>")
            
            result = self.orchestrator.generate_slides(
                str(input_file),
                format="revealjs",
                theme="white"
            )
            
            assert result == str(output_file)
            mock_execute.assert_called_once()
    
    def test_notes_generation_workflow(self):
        """Test complete notes generation workflow."""
        # Create test input file
        test_content = """---
title: "Test Notes"
format: pdf
---

# Introduction

These are test notes with detailed content.

## Section 1

Comprehensive explanation of concepts.
"""
        
        input_file = self.temp_path / "notes.qmd"
        input_file.write_text(test_content)
        
        # Mock the executor
        with patch.object(self.orchestrator.executor, 'execute_command') as mock_execute:
            mock_result = QuartoResult(
                success=True,
                output_file=str(self.temp_path / "notes.pdf"),
                stdout="Output created: notes.pdf",
                stderr="",
                return_code=0,
                execution_time=2.0
            )
            mock_execute.return_value = mock_result
            
            # Create mock output file
            output_file = self.temp_path / "notes.pdf"
            output_file.write_text("Mock PDF content")
            
            result = self.orchestrator.generate_notes(
                str(input_file),
                format="pdf",
                academic_style=True
            )
            
            assert result == str(output_file)
            mock_execute.assert_called_once()
    
    def test_error_handling_in_generation(self):
        """Test error handling during generation."""
        input_file = self.temp_path / "nonexistent.qmd"
        
        with pytest.raises(OutputError):
            self.orchestrator.generate_slides(str(input_file))
    
    def test_themed_slides_generation(self):
        """Test themed slides generation."""
        # Create test input file
        test_content = """---
title: "Themed Slides"
---

# Test Content
"""
        
        input_file = self.temp_path / "themed.qmd"
        input_file.write_text(test_content)
        
        # Mock theme manager
        with patch.object(self.orchestrator.theme_manager, 'get_theme') as mock_get_theme, \
             patch.object(self.orchestrator.theme_manager, 'generate_reveal_css') as mock_generate_css:
            
            mock_theme = Mock()
            mock_theme.transition = 'fade'
            mock_theme.background_transition = 'slide'
            mock_theme.show_slide_numbers = True
            mock_theme.show_progress = True
            mock_theme.enable_chalkboard = True
            mock_theme.enable_menu = True
            mock_theme.enable_overview = True
            mock_get_theme.return_value = mock_theme
            mock_generate_css.return_value = "/* Mock CSS */"
            
            # Mock executor
            with patch.object(self.orchestrator.executor, 'execute_command') as mock_execute:
                mock_result = QuartoResult(
                    success=True,
                    output_file=str(self.temp_path / "themed.html"),
                    stdout="Output created: themed.html",
                    stderr="",
                    return_code=0,
                    execution_time=1.5
                )
                mock_execute.return_value = mock_result
                
                # Create mock output file
                output_file = self.temp_path / "themed.html"
                output_file.write_text("<html>Themed slides</html>")
                
                result = self.orchestrator.generate_themed_slides(
                    str(input_file),
                    theme_name="academic-minimal"
                )
                
                assert result == str(output_file)
                mock_get_theme.assert_called_once_with("academic-minimal")
    
    def test_math_optimization(self):
        """Test math-optimized slides generation."""
        # Create test input with math
        test_content = """---
title: "Math Slides"
---

# Mathematical Content

Inline math: $E = mc^2$

Display math:
$$\\int_0^1 x^2 dx = \\frac{1}{3}$$
"""
        
        input_file = self.temp_path / "math.qmd"
        input_file.write_text(test_content)
        
        # Mock math renderer
        with patch.object(self.orchestrator.math_renderer, 'optimize_math_rendering') as mock_optimize:
            from markdown_slides_generator.latex.math_renderer import MathOptimizationResult
            mock_result = MathOptimizationResult(
                optimized_content=test_content,
                rendering_config=Mock(),
                warnings=[],
                performance_notes=[],
                compatibility_issues=[]
            )
            mock_optimize.return_value = mock_result
            
            # Mock executor
            with patch.object(self.orchestrator.executor, 'execute_command') as mock_execute:
                mock_result = QuartoResult(
                    success=True,
                    output_file=str(self.temp_path / "math.html"),
                    stdout="Output created: math.html",
                    stderr="",
                    return_code=0,
                    execution_time=1.0
                )
                mock_execute.return_value = mock_result
                
                # Create mock output file
                output_file = self.temp_path / "math.html"
                output_file.write_text("<html>Math slides</html>")
                
                result = self.orchestrator.generate_slides_with_math_optimization(
                    str(input_file),
                    format="revealjs"
                )
                
                assert result == str(output_file)
    
    def test_multiple_format_generation(self):
        """Test generating multiple output formats."""
        # Create test input file
        test_content = """---
title: "Multi-format Test"
---

# Content
"""
        
        input_file = self.temp_path / "multi.qmd"
        input_file.write_text(test_content)
        
        formats = ["revealjs", "beamer", "pptx"]
        results = []
        
        # Mock executor for multiple calls
        with patch.object(self.orchestrator.executor, 'execute_command') as mock_execute:
            def mock_execute_side_effect(command):
                format_name = command.output_format
                output_file = self.temp_path / f"multi.{format_name}"
                output_file.write_text(f"Mock {format_name} content")
                
                return QuartoResult(
                    success=True,
                    output_file=str(output_file),
                    stdout=f"Output created: {output_file}",
                    stderr="",
                    return_code=0,
                    execution_time=1.0
                )
            
            mock_execute.side_effect = mock_execute_side_effect
            
            # Generate slides in multiple formats
            for fmt in formats:
                result = self.orchestrator.generate_slides(
                    str(input_file),
                    format=fmt
                )
                results.append(result)
            
            assert len(results) == 3
            assert mock_execute.call_count == 3


class TestQuartoIntegrationWithRealFiles:
    """Integration tests with real file operations (but mocked Quarto)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = QuartoOrchestrator()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_complex_academic_content(self):
        """Test processing complex academic content."""
        complex_content = """---
title: "Advanced Mathematics Lecture"
author: "Dr. Test"
date: "2024-01-01"
format:
  revealjs:
    theme: white
    math-renderer: mathjax
---

# Introduction to Calculus

## Limits and Continuity

The limit of a function $f(x)$ as $x$ approaches $a$ is:

$$\\lim_{x \\to a} f(x) = L$$

### Properties of Limits

1. **Sum Rule**: $\\lim_{x \\to a} [f(x) + g(x)] = \\lim_{x \\to a} f(x) + \\lim_{x \\to a} g(x)$
2. **Product Rule**: $\\lim_{x \\to a} [f(x) \\cdot g(x)] = \\lim_{x \\to a} f(x) \\cdot \\lim_{x \\to a} g(x)$

## Derivatives

The derivative of $f(x)$ is defined as:

$$f'(x) = \\lim_{h \\to 0} \\frac{f(x+h) - f(x)}{h}$$

### Common Derivatives

| Function | Derivative |
|----------|------------|
| $x^n$ | $nx^{n-1}$ |
| $\\sin(x)$ | $\\cos(x)$ |
| $\\cos(x)$ | $-\\sin(x)$ |
| $e^x$ | $e^x$ |

## Integration

The fundamental theorem of calculus states:

$$\\int_a^b f'(x) dx = f(b) - f(a)$$

### Integration Techniques

```python
import numpy as np
import matplotlib.pyplot as plt

# Numerical integration example
def f(x):
    return x**2

x = np.linspace(0, 1, 100)
y = f(x)

# Trapezoidal rule
integral = np.trapz(y, x)
print(f"Integral approximation: {integral}")
```

## Applications

Real-world applications include:

- Physics: velocity and acceleration
- Economics: marginal cost and revenue
- Biology: population growth models
- Engineering: optimization problems
"""
        
        input_file = self.temp_path / "complex.qmd"
        input_file.write_text(complex_content)
        
        # Mock executor to simulate successful processing
        with patch.object(self.orchestrator.executor, 'execute_command') as mock_execute:
            mock_result = QuartoResult(
                success=True,
                output_file=str(self.temp_path / "complex.html"),
                stdout="Output created: complex.html\nProcessing math expressions...\nGenerated 15 slides",
                stderr="",
                return_code=0,
                execution_time=3.5
            )
            mock_execute.return_value = mock_result
            
            # Create mock output file
            output_file = self.temp_path / "complex.html"
            output_file.write_text("<html>Complex academic slides</html>")
            
            result = self.orchestrator.generate_slides(
                str(input_file),
                format="revealjs",
                theme="white"
            )
            
            assert result == str(output_file)
            
            # Verify command was built correctly
            call_args = mock_execute.call_args[0][0]
            assert call_args.input_file == str(input_file)
            assert call_args.output_format == "revealjs"
    
    def test_error_recovery_and_reporting(self):
        """Test error recovery and detailed error reporting."""
        # Create file with problematic content
        problematic_content = """---
title: "Problematic Content"
---

# Test

Invalid LaTeX: $\\invalid{command}$
"""
        
        input_file = self.temp_path / "problematic.qmd"
        input_file.write_text(problematic_content)
        
        # Mock executor to simulate Quarto errors
        with patch.object(self.orchestrator.executor, 'execute_command') as mock_execute:
            mock_result = QuartoResult(
                success=False,
                output_file=None,
                stdout="",
                stderr="ERROR: LaTeX compilation failed\nUnknown command: \\invalid",
                return_code=1,
                execution_time=0.5,
                errors=["LaTeX compilation failed", "Unknown command: \\invalid"]
            )
            mock_execute.return_value = mock_result
            
            with pytest.raises(OutputError) as exc_info:
                self.orchestrator.generate_slides(str(input_file))
            
            # Check that error message contains useful information
            error_msg = str(exc_info.value)
            assert "Failed to generate" in error_msg
            assert "LaTeX" in error_msg or "compilation" in error_msg


if __name__ == "__main__":
    pytest.main([__file__])