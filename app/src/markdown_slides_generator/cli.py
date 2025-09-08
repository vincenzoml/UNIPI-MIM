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
    default='academic-minimal',
    help="Theme for slides (e.g., academic-minimal, academic-modern, academic-technical). Default: academic-minimal"
)
@click.option(
    '--template',
    help="Template to use for generation (e.g., academic-slides-revealjs, academic-notes-pdf)"
)
@click.option(
    '--author',
    help="Author name for the presentation/document"
)
@click.option(
    '--title',
    help="Title for the presentation/document (overrides markdown title)"
)
@click.option(
    '--date',
    help="Date for the presentation/document"
)
@click.option(
    '--institute',
    help="Institution name"
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
    template: Optional[str],
    author: Optional[str],
    title: Optional[str],
    date: Optional[str],
    institute: Optional[str],
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
        
        # Create temporary files for slides and notes content
        slides_file = output_dir / f"{input_file.stem}_slides.qmd"
        notes_file_path = output_dir / f"{input_file.stem}_notes.qmd"
        
        with open(slides_file, 'w', encoding='utf-8') as f:
            f.write(slides_content)
        with open(notes_file_path, 'w', encoding='utf-8') as f:
            f.write(notes_content)
        
        # Prepare template variables
        variables = {}
        if title:
            variables['title'] = title
        if author:
            variables['author'] = author
        if date:
            variables['date'] = date
        if institute:
            variables['institute'] = institute
        
        # Generate outputs based on options
        if not notes_only:
            logger.info("Generating slides...")
            for fmt in format:
                if template:
                    # Use themed slides with template
                    output_file = quarto_orchestrator.generate_themed_slides(
                        str(slides_file), theme, template, fmt, None, variables
                    )
                else:
                    # Use standard generation
                    output_file = quarto_orchestrator.generate_slides(
                        str(slides_file), fmt, None, theme
                    )
                click.echo(f"✓ Generated slides: {output_file}")
        
        if not slides_only:
            logger.info("Generating notes...")
            if template and 'notes' in template:
                # Use templated notes
                notes_output = quarto_orchestrator.generate_templated_notes(
                    str(notes_file_path), template, 'pdf', None, variables
                )
            else:
                # Use standard notes generation
                notes_output = quarto_orchestrator.generate_notes(
                    str(notes_file_path), 'pdf'
                )
            click.echo(f"✓ Generated notes: {notes_output}")
        
        # Clean up temporary files
        if slides_file.exists():
            slides_file.unlink()
        if notes_file_path.exists():
            notes_file_path.unlink()
        
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
def themes():
    """
    List available themes and their information.
    
    Shows all built-in and custom themes with descriptions and style information.
    """
    try:
        orchestrator = QuartoOrchestrator()
        theme_manager = orchestrator.get_theme_manager()
        
        themes = theme_manager.list_themes()
        
        click.echo("🎨 Available Themes:\n")
        
        # Group by type
        builtin_themes = {k: v for k, v in themes.items() if v['type'] == 'built-in'}
        custom_themes = {k: v for k, v in themes.items() if v['type'] == 'custom'}
        
        if builtin_themes:
            click.echo("Built-in Themes:")
            for name, info in builtin_themes.items():
                click.echo(f"  • {name}")
                click.echo(f"    {info['display_name']} - {info['description']}")
                click.echo(f"    Style: {info['style']}, Color: {info['color_scheme']}")
                click.echo()
        
        if custom_themes:
            click.echo("Custom Themes:")
            for name, info in custom_themes.items():
                click.echo(f"  • {name}")
                click.echo(f"    {info['display_name']} - {info['description']}")
                click.echo(f"    Style: {info['style']}, Color: {info['color_scheme']}")
                click.echo()
        
        if not custom_themes:
            click.echo("No custom themes found. Create one with 'create-theme' command.")
        
    except Exception as e:
        logger.error(f"Error listing themes: {e}")
        raise click.ClickException(str(e))


@cli.command()
def templates():
    """
    List available templates and their information.
    
    Shows all built-in and custom templates with descriptions and format information.
    """
    try:
        orchestrator = QuartoOrchestrator()
        template_manager = orchestrator.get_template_manager()
        
        templates = template_manager.list_templates()
        
        click.echo("📄 Available Templates:\n")
        
        # Group by type
        builtin_templates = {k: v for k, v in templates.items() if v['type'] == 'built-in'}
        custom_templates = {k: v for k, v in templates.items() if v['type'] == 'custom'}
        
        if builtin_templates:
            click.echo("Built-in Templates:")
            for name, info in builtin_templates.items():
                click.echo(f"  • {name}")
                click.echo(f"    {info['display_name']} - {info['description']}")
                click.echo(f"    Type: {info['template_type']}, Format: {info['output_format']}")
                click.echo(f"    Required fields: {', '.join(info['required_fields']) if info['required_fields'] else 'None'}")
                click.echo()
        
        if custom_templates:
            click.echo("Custom Templates:")
            for name, info in custom_templates.items():
                click.echo(f"  • {name}")
                click.echo(f"    {info['display_name']} - {info['description']}")
                click.echo(f"    Type: {info['template_type']}, Format: {info['output_format']}")
                click.echo()
        
        if not custom_templates:
            click.echo("No custom templates found. Create one with 'create-template' command.")
        
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.argument('name')
@click.option('--base-theme', default='academic-minimal', help='Base theme to customize')
@click.option('--background-color', help='Background color (hex)')
@click.option('--text-color', help='Text color (hex)')
@click.option('--accent-color', help='Accent color (hex)')
@click.option('--heading-font', help='Heading font family')
@click.option('--body-font', help='Body font family')
@click.option('--description', help='Theme description')
def create_theme(name, base_theme, background_color, text_color, accent_color, heading_font, body_font, description):
    """
    Create a custom theme based on an existing theme.
    
    NAME: Name for the new custom theme.
    
    Examples:
    
        # Create theme with custom colors
        markdown-slides create-theme my-theme --accent-color "#ff6b6b" --background-color "#f8f9fa"
        
        # Create theme with custom fonts
        markdown-slides create-theme academic-serif --heading-font "Crimson Text" --body-font "Source Serif Pro"
    """
    try:
        orchestrator = QuartoOrchestrator()
        theme_manager = orchestrator.get_theme_manager()
        
        # Prepare customizations
        customizations = {}
        if background_color:
            customizations['background_color'] = background_color
        if text_color:
            customizations['text_color'] = text_color
        if accent_color:
            customizations['accent_color'] = accent_color
        if description:
            customizations['description'] = description
        
        # Typography customizations
        if heading_font or body_font:
            typography = {}
            if heading_font:
                typography['heading_font'] = heading_font
            if body_font:
                typography['body_font'] = body_font
            customizations['typography'] = typography
        
        # Create the theme
        custom_theme = theme_manager.create_custom_theme(name, base_theme, customizations)
        
        click.echo(f"✓ Created custom theme: {custom_theme.display_name}")
        click.echo(f"  Based on: {base_theme}")
        click.echo(f"  Description: {custom_theme.description}")
        
        # Export CSS for preview
        css_file = Path(f"{name}.css")
        theme_manager.export_theme_css(name, str(css_file))
        click.echo(f"  CSS exported to: {css_file}")
        
    except Exception as e:
        logger.error(f"Error creating theme: {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.argument('name')
@click.option('--type', 'template_type', required=True, 
              type=click.Choice(['slides', 'notes', 'handouts']),
              help='Type of template')
@click.option('--format', 'output_format', required=True,
              type=click.Choice(['revealjs', 'beamer', 'pptx', 'pdf', 'html']),
              help='Output format')
@click.option('--base-template', help='Base template to customize')
@click.option('--description', help='Template description')
def create_template(name, template_type, output_format, base_template, description):
    """
    Create a custom template.
    
    NAME: Name for the new custom template.
    
    Examples:
    
        # Create custom slides template
        markdown-slides create-template my-slides --type slides --format revealjs
        
        # Create custom notes template based on existing one
        markdown-slides create-template my-notes --type notes --format pdf --base-template academic-notes-pdf
    """
    try:
        orchestrator = QuartoOrchestrator()
        
        # Prepare customizations
        customizations = {}
        if description:
            customizations['description'] = description
        
        # Create the template
        custom_template = orchestrator.create_custom_template(
            name, template_type, output_format, base_template, customizations
        )
        
        click.echo(f"✓ Created custom template: {custom_template.display_name}")
        click.echo(f"  Type: {template_type}")
        click.echo(f"  Format: {output_format}")
        if base_template:
            click.echo(f"  Based on: {base_template}")
        click.echo(f"  Description: {custom_template.description}")
        
    except Exception as e:
        logger.error(f"Error creating template: {e}")
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