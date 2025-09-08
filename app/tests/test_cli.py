"""
Basic tests for CLI functionality - placeholder for task 1.

These are minimal tests to verify the project structure is working.
Comprehensive tests will be added in task 8.1 and 8.2.
"""

import pytest
from click.testing import CliRunner
from markdown_slides_generator.cli import cli


class TestCLI:
    """Test CLI basic functionality."""
    
    def test_cli_help(self):
        """Test that CLI help command works."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert 'Markdown Slides Generator' in result.output
        assert 'generate' in result.output
        assert 'batch' in result.output
        assert 'check' in result.output
    
    def test_cli_version(self):
        """Test that version command works."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        assert '0.1.0' in result.output
    
    def test_generate_help(self):
        """Test generate command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['generate', '--help'])
        
        assert result.exit_code == 0
        assert 'Generate slides and notes' in result.output
        assert 'INPUT_FILE' in result.output
    
    def test_batch_help(self):
        """Test batch command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['batch', '--help'])
        
        assert result.exit_code == 0
        assert 'Batch process' in result.output
        assert 'INPUT_DIR' in result.output
    
    def test_check_command(self):
        """Test check command runs without error."""
        runner = CliRunner()
        result = runner.invoke(cli, ['check'])
        
        assert result.exit_code == 0
        assert 'dependencies' in result.output.lower()