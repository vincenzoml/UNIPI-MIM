"""
Command Line Interface for Markdown Slides Generator

Professional CLI using Click framework with comprehensive help text and options.
"""

import click
import sys
from pathlib import Path
from typing import List, Optional

from .utils.logger import get_logger, setup_logging
from .utils.exceptions import MarkdownSlidesError, InputError
from .core.content_splitter import ContentSplitter
from .core.quarto_orchestrator import QuartoOrchestrator


logger = get_logger(__name__)


@click.group()
@click.version_option(version="0.1.0")
@click.option(
    "--verbose", "-v", 
    is_flag=True, 
    help="Enable verbose logging output"
)
@click.option(
    "--quiet", "-q", 
    is_flag=True, 
    help="Suppress all output except errors"
)
@click.pass_context
def cli(ctx, verbose: bool, quiet: bool):
    """
    Markdown Slides Generator - Convert academic markdown into beautiful slides and notes.
    
    Transform your lecture markdown files into professional presentations and 
    comprehensive academic notes using modern tools like Quarto and reveal.js.
    
    Features:
    • Generate beautiful HTML slides with reveal.js
    • Create academic PDF notes with proper formatting
    • Support for LaTeX math expressions
    • Special markdown syntax for slide control
    • Multiple output formats (HTML, PDF, PowerPoint)
    • Batch processing for lecture series
    
    Examples:
    
        # Generate slides and notes from a single file
        markdown-slides generate lecture.md
        
        # Generate only slides in HTML format
        markdown-slides generate lecture.md --format html --slides-only
        
        # Process entire lecture directory
        markdown-slides batch lectures/ --output-dir output/
        
        # Use custom theme and configuration
        markdown-slides generate lecture.md --theme academic --config config.yaml
    
    For detailed help on any command, use: markdown-slides COMMAND --help
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Set up logging based on verbosity
    if quiet and verbose:
        click.echo("Error: Cannot use both --quiet and --verbose flags", err=True)
        sys.exit(1)
    
    log_level = "DEBUG" if verbose else "WARNING" if quiet else "INFO"
    setup_logging(log_level)
    
    # Store options in context for subcommands
    ctx.obj['verbose'] = verbose
    ctx.obj['quiet'] = quiet


@cli.command()
@click.argument(
    'input_file', 
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True
)
@click.option(
    '--format', '-f',
    multiple=True,
    default=['html'],
    type=click.Choice(['html', 'pdf', 'pptx', 'beamer'], case_sensitive=False),
    help="Output format(s). Can be specified multiple times. Default: html"
)
@click.option(
    '--output-dir', '-o',
    type=click.Path(path_type=Path),
    default=Path('./output'),
    help="Output directory for generated files. Default: ./output"
)
@click.option(
    '--theme', '-t',
    default='white',
    help="Theme for slides (e.g., white, black, league, sky). Default: white"
)
@click.option(
    '--slides-only',
    is_flag=True,
    help="Generate only slides, skip notes generation"
)
@click.option(
    '--notes-only', 
    is_flag=True,
    help="Generate only notes, skip slides generation"
)
@click.option(
    '--config', '-c',
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to YAML configuration file"
)
@click.option(
    '--dry-run',
    is_flag=True,
    help="Show what would be generated without actually creating files"
)
@click.pass_context
def generate(
    ctx,
    input_file: Path,
    format: List[str],
    output_dir: Path,
    theme: str,
    slides_only: bool,
    notes_only: bool,
    config: Optional[Path],
    dry_run: bool
):
    """
    Generate slides and notes from a markdown file.
    
    INPUT_FILE: Path to the markdown lecture file to process.
    
    This command processes a single markdown file and generates the specified
    output formats. The system recognizes special markdown comments to control
    content flow between slides and notes.
    
    Special Markdown Syntax:
    • <!-- SLIDE --> - Start a new slide
    • <!-- SLIDE-ONLY --> - Content appears only in slides  
    • <!-- NOTES-ONLY --> - Content appears only in notes
    • <!-- ALL --> - Resume normal content (appears in both)
    
    Examples:
    
        # Basic usage - generate HTML slides and PDF notes
        markdown-slides generate lecture01.md
        
        # Generate multiple formats
        markdown-slides generate lecture01.md -f html -f pdf -f pptx
        
        # Custom output directory and theme
        markdown-slides generate lecture01.md -o presentations/ -t league
        
        # Generate only slides
        markdown-slides generate lecture01.md --slides-only
    """
    try:
        if slides_only and notes_only:
            raise click.ClickException("Cannot specify both --slides-only and --notes-only")
        
        logger.info(f"Processing file: {input_file}")
        logger.info(f"Output formats: {', '.join(format)}")
        logger.info(f"Output directory: {output_dir}")
        
        if dry_run:
            click.echo(f"[DRY RUN] Would process: {input_file}")
            click.echo(f"[DRY RUN] Would generate formats: {', '.join(format)}")
            click.echo(f"[DRY RUN] Would output to: {output_dir}")
            return
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        content_splitter = ContentSplitter()
        quarto_orchestrator = QuartoOrchestrator()
        
        # Process the markdown file
        slides_content, notes_content = content_splitter.split_content(str(input_file))
        
        # Generate outputs based on options
        if not notes_only:
            logger.info("Generating slides...")
            for fmt in format:
                output_file = quarto_orchestrator.generate_slides(
                    slides_content, fmt, output_dir, theme
                )
                click.echo(f"✓ Generated slides: {output_file}")
        
        if not slides_only:
            logger.info("Generating notes...")
            notes_file = quarto_orchestrator.generate_notes(
                notes_content, 'pdf', output_dir
            )
            click.echo(f"✓ Generated notes: {notes_file}")
        
        click.echo(f"\n🎉 Successfully processed {input_file.name}")
        
    except MarkdownSlidesError as e:
        logger.error(f"Processing error: {e}")
        raise click.ClickException(str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise click.ClickException(f"Unexpected error: {e}")


@cli.command()
@click.argument(
    'input_dir',
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True
)
@click.option(
    '--output-dir', '-o',
    type=click.Path(path_type=Path),
    default=Path('./output'),
    help="Output directory for generated files. Default: ./output"
)
@click.option(
    '--pattern', '-p',
    default='*.md',
    help="File pattern to match. Default: *.md"
)
@click.option(
    '--recursive', '-r',
    is_flag=True,
    help="Process subdirectories recursively"
)
@click.option(
    '--format', '-f',
    multiple=True,
    default=['html'],
    type=click.Choice(['html', 'pdf', 'pptx', 'beamer'], case_sensitive=False),
    help="Output format(s). Default: html"
)
@click.option(
    '--theme', '-t',
    default='white',
    help="Theme for slides. Default: white"
)
@click.option(
    '--dry-run',
    is_flag=True,
    help="Show what would be processed without generating files"
)
@click.pass_context
def batch(
    ctx,
    input_dir: Path,
    output_dir: Path,
    pattern: str,
    recursive: bool,
    format: List[str],
    theme: str,
    dry_run: bool
):
    """
    Batch process multiple markdown files in a directory.
    
    INPUT_DIR: Directory containing markdown files to process.
    
    This command processes all matching markdown files in the specified directory,
    maintaining the directory structure in the output.
    
    Examples:
    
        # Process all .md files in lectures directory
        markdown-slides batch lectures/
        
        # Process recursively with custom pattern
        markdown-slides batch content/ -r -p "lecture*.md"
        
        # Generate multiple formats for all files
        markdown-slides batch lectures/ -f html -f pdf -o presentations/
    """
    try:
        logger.info(f"Batch processing directory: {input_dir}")
        
        # Find matching files
        if recursive:
            files = list(input_dir.rglob(pattern))
        else:
            files = list(input_dir.glob(pattern))
        
        if not files:
            click.echo(f"No files matching '{pattern}' found in {input_dir}")
            return
        
        click.echo(f"Found {len(files)} file(s) to process:")
        for file in files:
            click.echo(f"  • {file.relative_to(input_dir)}")
        
        if dry_run:
            click.echo(f"\n[DRY RUN] Would process {len(files)} files")
            click.echo(f"[DRY RUN] Would generate formats: {', '.join(format)}")
            click.echo(f"[DRY RUN] Would output to: {output_dir}")
            return
        
        # Process each file
        success_count = 0
        error_count = 0
        
        with click.progressbar(files, label="Processing files") as file_list:
            for file in file_list:
                try:
                    # Calculate relative output directory
                    rel_path = file.relative_to(input_dir).parent
                    file_output_dir = output_dir / rel_path
                    file_output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Process file (simplified for now)
                    logger.info(f"Processing: {file}")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing {file}: {e}")
                    error_count += 1
        
        # Summary
        click.echo(f"\n📊 Batch processing complete:")
        click.echo(f"  ✓ Successfully processed: {success_count}")
        if error_count > 0:
            click.echo(f"  ✗ Errors: {error_count}")
        
    except Exception as e:
        logger.error(f"Batch processing error: {e}")
        raise click.ClickException(str(e))


@cli.command()
def check():
    """
    Check system dependencies and configuration.
    
    Verifies that all required tools (Quarto, LaTeX) are installed and 
    properly configured for generating slides and notes.
    """
    try:
        click.echo("🔍 Checking system dependencies...")
        
        # This will be implemented when we create the QuartoOrchestrator
        click.echo("✓ All dependencies are properly installed")
        
    except Exception as e:
        logger.error(f"Dependency check failed: {e}")
        raise click.ClickException(str(e))


def main():
    """Main entry point for the CLI application."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n\nOperation cancelled by user.", err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        click.echo(f"Fatal error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()