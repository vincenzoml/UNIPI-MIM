"""
Tests for Quarto Orchestrator - Task 3.1 Implementation

Tests the comprehensive Quarto command interface with format-specific optimizations,
robust error handling, and parsing of Quarto output messages.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess

from src.markdown_slides_generator.core.quarto_orchestrator import (
    QuartoOrchestrator,
    QuartoCommandBuilder,
    QuartoExecutor,
    QuartoCommand,
    QuartoResult,
    OutputFormat
)
from src.markdown_slides_generator.utils.exceptions import OutputError


class TestQuartoCommandBuilder:
    """Test the Quarto command builder with format-specific optimizations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.builder = QuartoCommandBuilder()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test.qmd"
        self.test_file.write_text("# Test Content\n\nSome content here.")
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_build_revealjs_command(self):
        """Test building reveal.js command with optimizations."""
        command = self.builder.build_command(
            input_file=str(self.test_file),
            output_format=OutputFormat.REVEALJS,
            custom_config={'theme': 'dark', 'slide-number': True}
        )
        
        assert command.input_file == str(self.test_file)
        assert command.output_format == "revealjs"
        assert 'quarto' in command.args
        assert 'render' in command.args
        assert '--to' in command.args
        assert 'revealjs' in command.args
        # Quarto uses YAML frontmatter for configuration, not command-line args
        # This is the correct modern approach
    
    def test_build_beamer_command(self):
        """Test building Beamer command with academic optimizations."""
        command = self.builder.build_command(
            input_file=str(self.test_file),
            output_format=OutputFormat.BEAMER,
            custom_config={'theme': 'Berlin', 'aspectratio': '169'}
        )
        
        assert command.output_format == "beamer"
        # Quarto uses YAML frontmatter for themes and configuration
        assert 'quarto' in command.args
        assert 'render' in command.args
        assert '--to' in command.args
    
    def test_build_pptx_command(self):
        """Test building PowerPoint command."""
        command = self.builder.build_command(
            input_file=str(self.test_file),
            output_format=OutputFormat.PPTX,
            output_file="output.pptx"
        )
        
        assert command.output_format == "pptx"
        assert '--output' in command.args
        assert 'output.pptx' in command.args
        # Slide level is configured in YAML, not command line
    
    def test_build_pdf_notes_command(self):
        """Test building PDF notes command with academic formatting."""
        command = self.builder.build_command(
            input_file=str(self.test_file),
            output_format=OutputFormat.PDF,
            custom_config={'documentclass': 'article', 'toc': True}
        )
        
        assert command.output_format == "pdf"
        # Document class, TOC, and PDF engine are configured in YAML frontmatter
        assert 'quarto' in command.args
        assert 'render' in command.args
    
    def test_build_html_notes_command(self):
        """Test building HTML notes command."""
        command = self.builder.build_command(
            input_file=str(self.test_file),
            output_format=OutputFormat.HTML,
            custom_config={'theme': 'cosmo', 'toc-depth': 3}
        )
        
        assert command.output_format == "html"
        # Theme and TOC depth are configured in YAML frontmatter
        assert 'quarto' in command.args
        assert 'render' in command.args
    
    def test_slides_command_builder(self):
        """Test the specialized slides command builder."""
        command = self.builder.build_slides_command(
            input_file=str(self.test_file),
            format="revealjs",
            theme="white",
            custom_options={'chalkboard': True}
        )
        
        assert command.output_format == "revealjs"
        # Theme is configured in YAML frontmatter
        assert 'quarto' in command.args
    
    def test_notes_command_builder(self):
        """Test the specialized notes command builder."""
        command = self.builder.build_notes_command(
            input_file=str(self.test_file),
            format="pdf",
            academic_style=True,
            custom_options={'fontsize': '12pt'}
        )
        
        assert command.output_format == "pdf"
        # Academic formatting options are configured in YAML frontmatter
        assert 'quarto' in command.args
        assert 'render' in command.args
    
    def test_config_to_args_conversion(self):
        """Test configuration dictionary to command line arguments conversion."""
        config = {
            'theme': 'white',  # Should be in frontmatter, not CLI
            'slide-number': True,  # Valid CLI flag
            'incremental': False,  # False values should not be included
            'fontsize': '11pt',  # Should be in frontmatter, not CLI  
            'chalkboard': True,  # Valid CLI flag
            'help': True,  # Should NOT be CLI flag (causes --help issue)
            'nested_config': {'key': 'value'}  # Should be ignored
        }
        
        args = self.builder._config_to_args(config, OutputFormat.REVEALJS)
        
        # With the fix, NO RevealJS-specific CLI flags should be included
        # All RevealJS options should be set in the document's YAML frontmatter
        
        # These CLI flags should NOT be included (set in frontmatter instead)
        assert '--slide-number' not in args
        assert '--chalkboard' not in args
        assert '--theme' not in args
        assert 'white' not in args
        assert '--fontsize' not in args
        assert '11pt' not in args
        
        # False values and invalid flags should not be included
        assert '--incremental' not in args
        assert '--help' not in args  # This was causing the original bug
        assert '--nested_config' not in args
        
        # The args should be minimal - only the basic command structure
        # No format-specific CLI flags should be present


class TestQuartoExecutor:
    """Test the Quarto command executor with error handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test.qmd"
        self.test_file.write_text("# Test\n\nContent")
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    @patch('subprocess.run')
    def test_quarto_installation_check(self, mock_run):
        """Test Quarto installation verification."""
        # Mock successful version check
        mock_run.return_value = Mock(
            returncode=0,
            stdout="1.4.0\n",
            stderr=""
        )
        
        executor = QuartoExecutor()
        # Should not raise an exception
        assert executor is not None
        
        mock_run.assert_called_with(
            ['quarto', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
    
    @patch('subprocess.run')
    def test_quarto_not_found(self, mock_run):
        """Test handling when Quarto is not installed."""
        mock_run.side_effect = FileNotFoundError()
        
        with pytest.raises(OutputError, match="Quarto not found"):
            QuartoExecutor()
    
    @patch('subprocess.run')
    def test_successful_command_execution(self, mock_run):
        """Test successful Quarto command execution."""
        # Mock version check
        mock_run.return_value = Mock(returncode=0, stdout="1.4.0\n", stderr="")
        executor = QuartoExecutor()
        
        # Mock successful render command
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Output created: test.html\n",
            stderr=""
        )
        
        command = QuartoCommand(
            input_file=str(self.test_file),
            output_format="revealjs",
            args=['quarto', 'render', str(self.test_file), '--to', 'revealjs']
        )
        
        result = executor.execute_command(command)
        
        assert result.success is True
        assert result.return_code == 0
        assert len(result.errors) == 0
        assert "Output created: test.html" in result.stdout
    
    @patch('subprocess.run')
    def test_failed_command_execution(self, mock_run):
        """Test handling of failed Quarto command execution."""
        # Mock version check
        mock_run.return_value = Mock(returncode=0, stdout="1.4.0\n", stderr="")
        executor = QuartoExecutor()
        
        # Mock failed render command
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="ERROR: File not found\n"
        )
        
        command = QuartoCommand(
            input_file="nonexistent.qmd",
            output_format="revealjs",
            args=['quarto', 'render', 'nonexistent.qmd', '--to', 'revealjs']
        )
        
        result = executor.execute_command(command)
        
        assert result.success is False
        assert result.return_code == 1
        assert len(result.errors) > 0
        assert "ERROR: File not found" in result.stderr
    
    @patch('subprocess.run')
    def test_command_timeout(self, mock_run):
        """Test handling of command timeout."""
        # Mock version check
        mock_run.return_value = Mock(returncode=0, stdout="1.4.0\n", stderr="")
        executor = QuartoExecutor()
        
        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired(['quarto'], 1)
        
        command = QuartoCommand(
            input_file=str(self.test_file),
            output_format="revealjs",
            args=['quarto', 'render', str(self.test_file)]
        )
        
        result = executor.execute_command(command, timeout=1)
        
        assert result.success is False
        assert result.return_code == -1
        assert "timed out" in result.stderr
    
    def test_parse_quarto_output(self):
        """Test parsing of Quarto output for warnings and errors."""
        executor = QuartoExecutor.__new__(QuartoExecutor)  # Skip __init__
        
        stdout = """
        Processing file...
        WARNING: Deprecated option used
        Rendering...
        Output created: test.html
        """
        
        stderr = """
        ERROR: LaTeX compilation failed
        Warning: Missing reference
        """
        
        warnings, errors = executor._parse_quarto_output(stdout, stderr)
        
        assert len(warnings) >= 1
        assert len(errors) >= 1
        assert any("WARNING" in w for w in warnings)
        assert any("ERROR" in e for e in errors)
    
    def test_find_output_file(self):
        """Test finding output file from command and stdout."""
        executor = QuartoExecutor.__new__(QuartoExecutor)  # Skip __init__
        
        # Create a test output file
        output_file = self.temp_dir / "test.html"
        output_file.write_text("<html></html>")
        
        command = QuartoCommand(
            input_file=str(self.test_file),
            output_format="revealjs",
            output_file=str(output_file)
        )
        
        stdout = f"Output created: {output_file}\n"
        
        found_file = executor._find_output_file(command, stdout)
        
        assert found_file == str(output_file.absolute())


class TestQuartoOrchestrator:
    """Test the high-level Quarto orchestrator interface."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test.qmd"
        self.test_file.write_text("""---
title: Test Slides
format: revealjs
---

# Introduction

This is a test slide.

## Content

Some content here.
""")
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    @patch('src.markdown_slides_generator.core.quarto_orchestrator.QuartoExecutor')
    def test_generate_slides_success(self, mock_executor_class):
        """Test successful slide generation."""
        # Mock executor
        mock_executor = Mock()
        mock_executor_class.return_value = mock_executor
        
        # Mock successful result
        mock_result = QuartoResult(
            success=True,
            output_file=str(self.temp_dir / "test.html"),
            stdout="Output created: test.html",
            stderr="",
            return_code=0,
            execution_time=2.5,
            warnings=[],
            errors=[]
        )
        mock_executor.execute_command.return_value = mock_result
        
        orchestrator = QuartoOrchestrator()
        
        output_file = orchestrator.generate_slides(
            input_file=str(self.test_file),
            format="revealjs",
            theme="white"
        )
        
        assert output_file == str(self.temp_dir / "test.html")
        mock_executor.execute_command.assert_called_once()
    
    @patch('src.markdown_slides_generator.core.quarto_orchestrator.QuartoExecutor')
    def test_generate_slides_failure(self, mock_executor_class):
        """Test handling of slide generation failure."""
        # Mock executor
        mock_executor = Mock()
        mock_executor_class.return_value = mock_executor
        
        # Mock failed result
        mock_result = QuartoResult(
            success=False,
            output_file=None,
            stdout="",
            stderr="ERROR: Compilation failed",
            return_code=1,
            execution_time=1.0,
            warnings=[],
            errors=["ERROR: Compilation failed"]
        )
        mock_executor.execute_command.return_value = mock_result
        
        orchestrator = QuartoOrchestrator()
        
        with pytest.raises(OutputError, match="Failed to generate revealjs slides"):
            orchestrator.generate_slides(
                input_file=str(self.test_file),
                format="revealjs"
            )
    
    def test_generate_slides_file_not_found(self):
        """Test handling when input file doesn't exist."""
        orchestrator = QuartoOrchestrator()
        
        with pytest.raises(OutputError, match="Input file not found"):
            orchestrator.generate_slides(
                input_file="nonexistent.qmd",
                format="revealjs"
            )
    
    @patch('src.markdown_slides_generator.core.quarto_orchestrator.QuartoExecutor')
    def test_generate_notes_success(self, mock_executor_class):
        """Test successful notes generation."""
        # Mock executor
        mock_executor = Mock()
        mock_executor_class.return_value = mock_executor
        
        # Mock successful result
        mock_result = QuartoResult(
            success=True,
            output_file=str(self.temp_dir / "test.pdf"),
            stdout="Output created: test.pdf",
            stderr="",
            return_code=0,
            execution_time=3.2,
            warnings=[],
            errors=[]
        )
        mock_executor.execute_command.return_value = mock_result
        
        orchestrator = QuartoOrchestrator()
        
        output_file = orchestrator.generate_notes(
            input_file=str(self.test_file),
            format="pdf",
            academic_style=True
        )
        
        assert output_file == str(self.temp_dir / "test.pdf")
        mock_executor.execute_command.assert_called_once()
    
    def test_get_supported_formats(self):
        """Test getting supported output formats."""
        orchestrator = QuartoOrchestrator()
        
        formats = orchestrator.get_supported_formats()
        
        assert 'slides' in formats
        assert 'notes' in formats
        assert 'revealjs' in formats['slides']
        assert 'beamer' in formats['slides']
        assert 'pptx' in formats['slides']
        assert 'pdf' in formats['notes']
        assert 'html' in formats['notes']
    
    @patch('src.markdown_slides_generator.core.quarto_orchestrator.QuartoExecutor')
    def test_execution_summary(self, mock_executor_class):
        """Test getting execution summary."""
        # Mock executor
        mock_executor = Mock()
        mock_executor_class.return_value = mock_executor
        
        # Mock successful result
        mock_result = QuartoResult(
            success=True,
            output_file=str(self.temp_dir / "test.html"),
            stdout="Output created: test.html",
            stderr="",
            return_code=0,
            execution_time=2.5,
            warnings=[],
            errors=[]
        )
        mock_executor.execute_command.return_value = mock_result
        
        orchestrator = QuartoOrchestrator()
        
        # Generate slides to populate results
        orchestrator.generate_slides(
            input_file=str(self.test_file),
            format="revealjs"
        )
        
        summary = orchestrator.get_execution_summary()
        
        assert summary['total_executions'] == 1
        assert summary['successful'] == 1
        assert summary['failed'] == 0
        assert summary['total_time'] == 2.5
        assert 'slides_revealjs' in summary['results']
    
    def test_create_quarto_config(self):
        """Test basic Quarto configuration creation."""
        orchestrator = QuartoOrchestrator()
        
        config = {
            'format': {
                'revealjs': {
                    'theme': 'white',
                    'slide-number': True
                }
            }
        }
        
        yaml_config = orchestrator.create_quarto_config(config)
        
        assert 'project:' in yaml_config
        assert 'format:' in yaml_config
        assert 'revealjs:' in yaml_config


class TestOutputFormatEnum:
    """Test the OutputFormat enumeration."""
    
    def test_format_values(self):
        """Test that format enum has correct values."""
        assert OutputFormat.REVEALJS.value == "revealjs"
        assert OutputFormat.BEAMER.value == "beamer"
        assert OutputFormat.PPTX.value == "pptx"
        assert OutputFormat.PDF.value == "pdf"
        assert OutputFormat.HTML.value == "html"
    
    def test_format_from_string(self):
        """Test creating format enum from string."""
        assert OutputFormat("revealjs") == OutputFormat.REVEALJS
        assert OutputFormat("beamer") == OutputFormat.BEAMER
        assert OutputFormat("pptx") == OutputFormat.PPTX
        assert OutputFormat("pdf") == OutputFormat.PDF
        assert OutputFormat("html") == OutputFormat.HTML


class TestQuartoCommandDataClass:
    """Test the QuartoCommand data class."""
    
    def test_command_creation(self):
        """Test creating QuartoCommand with all parameters."""
        command = QuartoCommand(
            input_file="test.qmd",
            output_format="revealjs",
            output_file="output.html",
            args=['quarto', 'render', 'test.qmd'],
            env_vars={'QUARTO_PROJECT_DIR': '/path/to/project'}
        )
        
        assert command.input_file == "test.qmd"
        assert command.output_format == "revealjs"
        assert command.output_file == "output.html"
        assert command.args == ['quarto', 'render', 'test.qmd']
        assert command.env_vars == {'QUARTO_PROJECT_DIR': '/path/to/project'}
    
    def test_command_defaults(self):
        """Test QuartoCommand with default values."""
        command = QuartoCommand(
            input_file="test.qmd",
            output_format="revealjs"
        )
        
        assert command.args == []
        assert command.env_vars == {}


class TestQuartoResultDataClass:
    """Test the QuartoResult data class."""
    
    def test_result_creation(self):
        """Test creating QuartoResult with all parameters."""
        result = QuartoResult(
            success=True,
            output_file="output.html",
            stdout="Output created",
            stderr="",
            return_code=0,
            execution_time=2.5,
            warnings=["Warning message"],
            errors=[]
        )
        
        assert result.success is True
        assert result.output_file == "output.html"
        assert result.stdout == "Output created"
        assert result.stderr == ""
        assert result.return_code == 0
        assert result.execution_time == 2.5
        assert result.warnings == ["Warning message"]
        assert result.errors == []
    
    def test_result_defaults(self):
        """Test QuartoResult with default values."""
        result = QuartoResult(
            success=False,
            output_file=None,
            stdout="",
            stderr="Error occurred",
            return_code=1,
            execution_time=1.0
        )
        
        assert result.warnings == []
        assert result.errors == []