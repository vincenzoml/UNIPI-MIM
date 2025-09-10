"""
Command Line Interface for Markdown Slides Generator

Professional CLI using Click framework with comprehensive help text and options.
"""

import click
import sys
import os
import time
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml

from .utils.logger import get_logger, setup_logging
from .utils.exceptions import MarkdownSlidesError, InputError, ConfigurationError
from .utils.watchdog_utils import create_file_watcher
from .utils.live_server import start_live_server
from .core.content_splitter import ContentSplitter
from .core.quarto_orchestrator import QuartoOrchestrator
from .config import ConfigManager, Config


logger = get_logger(__name__)
config_manager = ConfigManager()


def _perform_generation(
    input_file: Path,
    final_config: Config,
    output_dir: Path,
    theme: str,
    template: Optional[str],
    title: Optional[str],
    author: Optional[str],
    date: Optional[str],
    institute: Optional[str],
    slides_only: bool,
    notes_only: bool,
    overwrite: bool,
    progress: bool,
    ctx
) -> List[str]:
    """
    Internal function to perform the actual generation.
    
    Returns:
        List of generated file paths
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize components
    content_splitter = ContentSplitter()
    quarto_orchestrator = QuartoOrchestrator()
    
    # Show progress if enabled
    if progress and not ctx.obj.get('quiet', False):
        click.echo("📝 Processing markdown content...")
    
    # Process the markdown file
    slides_content, notes_content = content_splitter.split_content(str(input_file))
    
    # Create temporary files for slides and notes content
    slides_file = output_dir / f"{input_file.stem}_slides.qmd"
    notes_file_path = output_dir / f"{input_file.stem}_notes.qmd"
    
    # Generate proper YAML frontmatter with all RevealJS options
    slides_frontmatter = quarto_orchestrator.generate_revealjs_frontmatter(
        final_config.slides.__dict__, theme
    )

    # Determine notes format(s) from configuration (allowing override)
    notes_formats = getattr(final_config.notes, 'formats', None) or ['pdf']
    # Use the first requested notes format as the primary output
    notes_primary_format = notes_formats[0]
    # Generate simple notes frontmatter using the selected format
    notes_frontmatter = f"---\nformat: {notes_primary_format}\n---\n\n"

    with open(slides_file, 'w', encoding='utf-8') as f:
        f.write(slides_frontmatter + slides_content)
    
    # Debug: log the frontmatter content
    logger.debug(f"Generated slides frontmatter:\n{slides_frontmatter}")
    with open(notes_file_path, 'w', encoding='utf-8') as f:
        f.write(notes_frontmatter + notes_content)
    
    # Prepare template variables from config and CLI
    variables = dict(final_config.variables)
    if title:
        variables['title'] = title
    if author:
        variables['author'] = author
    if date:
        variables['date'] = date
    if institute:
        variables['institute'] = institute
    
    generated_files = []
    
    # Generate outputs based on options
    if not notes_only:
        if progress and not ctx.obj.get('quiet', False):
            click.echo("🎨 Generating slides...")
        
        for fmt in final_config.output.formats:
            try:
                # Check if theme is a built-in application theme
                is_builtin_theme = theme in [t for t in quarto_orchestrator.theme_manager.list_themes().keys()]
                
                if template or is_builtin_theme:
                    # For built-in themes, we need to generate the frontmatter within generate_themed_slides
                    # to include the correct CSS path
                    # Convert 'html' format to 'revealjs' for proper slide generation
                    slide_format = 'revealjs' if fmt == 'html' else fmt
                    output_file = quarto_orchestrator.generate_themed_slides(
                        str(slides_file), theme, template, slide_format, None, variables, 
                        slides_config=final_config.slides.__dict__
                    )
                else:
                    # Use standard generation (for RevealJS standard themes)
                    # Convert 'html' format to 'revealjs' for proper slide generation  
                    slide_format = 'revealjs' if fmt == 'html' else fmt
                    output_file = quarto_orchestrator.generate_slides(
                        str(slides_file), slide_format, None, theme
                    )
                generated_files.append(output_file)
                click.echo(f"✓ Generated slides ({fmt}): {Path(output_file).name}")
            except Exception as e:
                logger.error(f"Error generating {fmt} slides: {e}")
                click.echo(f"✗ Failed to generate {fmt} slides: {e}", err=True)
    
    if not slides_only:
        if progress and not ctx.obj.get('quiet', False):
            click.echo("📚 Generating notes...")
        
        try:
            # Decide notes generation format(s) and trigger generation for primary
            # If template explicitly targets notes, prefer templated generation
            if template and 'notes' in template:
                notes_output = quarto_orchestrator.generate_templated_notes(
                    str(notes_file_path), template, notes_primary_format, None, variables
                )
            else:
                # Use standard notes generation with configured primary format
                notes_output = quarto_orchestrator.generate_notes(
                    str(notes_file_path), notes_primary_format
                )
            generated_files.append(notes_output)
            click.echo(f"✓ Generated notes: {Path(notes_output).name}")
        except Exception as e:
            logger.error(f"Error generating notes: {e}")
            click.echo(f"✗ Failed to generate notes: {e}", err=True)
    
    # Clean up temporary files
    if slides_file.exists():
        slides_file.unlink()
    if notes_file_path.exists():
        notes_file_path.unlink()
    
    return generated_files


async def _async_watch_with_serve(
    input_file: Path,
    final_config: Config,
    output_dir: Path,
    theme: str,
    template: Optional[str],
    title: Optional[str],
    author: Optional[str],
    date: Optional[str],
    institute: Optional[str],
    slides_only: bool,
    notes_only: bool,
    progress: bool,
    ctx,
    port: int,
    auto_open: bool
) -> None:
    """
    Async watch mode with live server support.
    """
    from concurrent.futures import ThreadPoolExecutor
    import threading
    
    # Start the live server
    try:
        live_server = await start_live_server(output_dir, port, auto_open)
        actual_port = live_server.port  # Use the actual port the server is running on
        click.echo(f"\n👁️  Watch mode with live server enabled.")
        click.echo(f"🌐 Server: http://localhost:{actual_port}")
        click.echo(f"📁 Serving: {output_dir}")
        click.echo("Press Ctrl+C to stop.")
        
        # Create a thread-safe way to communicate between file watcher and async server
        reload_event = asyncio.Event()
        
        # Get the current event loop so we can reference it from the thread
        main_loop = asyncio.get_running_loop()
        
        def regenerate_on_change(changed_file: Path) -> None:
            """Callback function to regenerate files when input changes."""
            # Only regenerate if the changed file is our input file
            if changed_file.resolve() == input_file.resolve():
                click.echo(f"\n🔄 Change detected in {changed_file.name}, regenerating...")
                try:
                    # Re-run the generation process with the same parameters
                    _perform_generation(
                        input_file=input_file,
                        final_config=final_config,
                        output_dir=output_dir,
                        theme=theme,
                        template=template,
                        title=title,
                        author=author,
                        date=date,
                        institute=institute,
                        slides_only=slides_only,
                        notes_only=notes_only,
                        overwrite=True,  # Always overwrite in watch mode
                        progress=progress,
                        ctx=ctx
                    )
                    click.echo(f"✓ Regeneration complete at {time.strftime('%H:%M:%S')}")
                    
                    # Signal that we need to reload the browser using thread-safe call
                    main_loop.call_soon_threadsafe(reload_event.set)
                    
                except Exception as e:
                    click.echo(f"✗ Error during regeneration: {e}", err=True)
                    logger.error(f"Watch mode regeneration error: {e}")
        
        # Start file watcher in a separate thread
        def run_file_watcher():
            try:
                with create_file_watcher(regenerate_on_change, debounce_seconds=2.0) as watcher:
                    watcher.watch_file(input_file)
                    watcher.start()
                    watcher.wait()
            except Exception as e:
                logger.error(f"File watcher error: {e}")
        
        # Start file watcher thread
        with ThreadPoolExecutor(max_workers=1) as executor:
            watcher_future = executor.submit(run_file_watcher)
            
            try:
                # Main async loop - wait for reload events and broadcast them
                while True:
                    await reload_event.wait()
                    reload_event.clear()
                    
                    # Broadcast reload to all connected browsers
                    await live_server.broadcast_reload()
                    click.echo("🔄 Browser reload triggered")
                    
            except KeyboardInterrupt:
                click.echo(f"\n👋 Stopping watch mode and server...")
            except Exception as e:
                click.echo(f"\n❌ Server error: {e}", err=True)
                logger.error(f"Live server error: {e}")
            finally:
                # Stop the live server
                await live_server.stop()
                
                # The file watcher will stop when we exit the context
                
    except Exception as e:
        click.echo(f"❌ Failed to start live server: {e}", err=True)
        logger.error(f"Live server startup error: {e}")


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
    • Watch mode for automatic regeneration on file changes
    
    Examples:
    
        # Generate slides and notes from a single file
        markdown-slides generate lecture.md
        
        # Generate only slides in HTML format
        markdown-slides generate lecture.md --format html --slides-only
        
        # Process entire lecture directory
        markdown-slides batch lectures/ --output-dir output/
        
        # Use custom theme and configuration
        markdown-slides generate lecture.md --theme academic --config config.yaml
        
        # Watch mode for development - regenerate on file changes
        markdown-slides generate lecture.md --watch
    
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
    type=click.Choice(['html', 'pdf', 'pptx', 'beamer'], case_sensitive=False),
    help="Output format(s). Can be specified multiple times. Default from config or html"
)
@click.option(
    '--output-dir', '-o',
    type=click.Path(path_type=Path),
    help="Output directory for generated files. Default from config or ./output"
)
@click.option(
    '--theme', '-t',
    help="Theme for slides. Default from config or academic-minimal"
)
@click.option(
    '--template',
    help="Template to use for generation"
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
    '--save-config',
    type=click.Path(path_type=Path),
    help="Save current options as configuration file"
)
@click.option(
    '--dry-run',
    is_flag=True,
    help="Show what would be generated without actually creating files"
)
@click.option(
    '--overwrite',
    is_flag=True,
    help="Overwrite existing output files"
)
@click.option(
    '--progress/--no-progress',
    default=True,
    help="Show progress indicators"
)
@click.option(
    '--watch', '-w',
    is_flag=True,
    help="Watch the input file for changes and regenerate automatically"
)
@click.option(
    '--serve', '-s',
    is_flag=True,
    help="Start a local server with auto-reload (requires --watch)"
)
@click.option(
    '--port', '-p',
    type=int,
    default=8000,
    help="Port for the local server (default: 8000)"
)
@click.option(
    '--no-open',
    is_flag=True,
    help="Don't automatically open browser when serving"
)
@click.pass_context
def generate(
    ctx,
    input_file: Path,
    format: List[str],
    output_dir: Optional[Path],
    theme: Optional[str],
    template: Optional[str],
    author: Optional[str],
    title: Optional[str],
    date: Optional[str],
    institute: Optional[str],
    slides_only: bool,
    notes_only: bool,
    config: Optional[Path],
    save_config: Optional[Path],
    dry_run: bool,
    overwrite: bool,
    progress: bool,
    watch: bool,
    serve: bool,
    port: int,
    no_open: bool
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
        markdown-slides generate lecture01.md -o presentations/ -t academic-modern
        
        # Generate only slides with custom config
        markdown-slides generate lecture01.md --slides-only -c my-config.yaml
        
        # Watch file for changes and regenerate automatically  
        markdown-slides generate lecture01.md --watch
        
        # Watch mode with live server and auto-reload in browser
        markdown-slides generate lecture01.md --watch --serve
        
        # Save current options as config for reuse
        markdown-slides generate lecture01.md -f html -f pdf --save-config my-settings.yaml
    """
    try:
        if slides_only and notes_only:
            raise click.ClickException("Cannot specify both --slides-only and --notes-only")
        
        if watch and dry_run:
            raise click.ClickException("Cannot use --watch with --dry-run")
        
        if serve and not watch:
            raise click.ClickException("--serve requires --watch mode")
        
        if serve and notes_only:
            raise click.ClickException("--serve is not compatible with --notes-only (notes are PDFs, not HTML)")
        
        # Load configuration
        try:
            base_config = config_manager.load_config(config)
        except ConfigurationError as e:
            raise click.ClickException(f"Configuration error: {e}")
        
        # Merge CLI options with configuration
        cli_options = {
            'format': format if format else None,
            'output_dir': str(output_dir) if output_dir else None,
            'theme': theme,
            'template': template,
            'author': author,
            'title': title,
            'date': date,
            'institute': institute,
            'verbose': ctx.obj.get('verbose', False),
            'quiet': ctx.obj.get('quiet', False),
        }
        
        # Remove None values
        cli_options = {k: v for k, v in cli_options.items() if v is not None}
        
        # Merge configurations
        final_config = config_manager.merge_cli_options(base_config, cli_options)
        
        # Apply defaults if not set
        if not final_config.output.formats:
            final_config.output.formats = ['html']
        if not output_dir:
            output_dir = Path(final_config.output.directory)
        if not theme:
            theme = final_config.slides.theme
        
        # Save configuration if requested
        if save_config:
            try:
                config_manager.save_config(final_config, save_config)
                click.echo(f"✓ Configuration saved to: {save_config}")
            except ConfigurationError as e:
                click.echo(f"Warning: Could not save configuration: {e}", err=True)
        
        # Setup logging based on final config
        setup_logging(final_config.logging.level)
        
        logger.info(f"Processing file: {input_file}")
        logger.info(f"Output formats: {', '.join(final_config.output.formats)}")
        logger.info(f"Output directory: {output_dir}")
        logger.info(f"Theme: {theme}")
        
        if dry_run:
            click.echo(f"[DRY RUN] Configuration:")
            click.echo(f"  Input file: {input_file}")
            click.echo(f"  Output formats: {', '.join(final_config.output.formats)}")
            click.echo(f"  Output directory: {output_dir}")
            click.echo(f"  Theme: {theme}")
            click.echo(f"  Template: {template or 'default'}")
            click.echo(f"  Slides only: {slides_only}")
            click.echo(f"  Notes only: {notes_only}")
            click.echo(f"  Overwrite: {overwrite}")
            return
        
        # Check for existing files if not overwriting
        if not overwrite and not final_config.output.overwrite:
            existing_files = []
            for fmt in final_config.output.formats:
                potential_files = [
                    output_dir / f"{input_file.stem}_slides.{fmt}",
                    output_dir / f"{input_file.stem}_notes.{fmt}",
                ]
                existing_files.extend([f for f in potential_files if f.exists()])
            
            if existing_files:
                click.echo("Warning: The following files already exist:")
                for f in existing_files:
                    click.echo(f"  • {f}")
                if not click.confirm("Overwrite existing files?"):
                    click.echo("Operation cancelled.")
                    return
        
        # Perform the actual generation
        generated_files = _perform_generation(
            input_file=input_file,
            final_config=final_config,
            output_dir=output_dir,
            theme=theme,
            template=template,
            title=title,
            author=author,
            date=date,
            institute=institute,
            slides_only=slides_only,
            notes_only=notes_only,
            overwrite=overwrite,
            progress=progress,
            ctx=ctx
        )
        
        # Summary
        if generated_files:
            click.echo(f"\n🎉 Successfully processed {input_file.name}")
            click.echo(f"📁 Output directory: {output_dir}")
            click.echo(f"📄 Generated {len(generated_files)} file(s)")
        else:
            click.echo(f"\n⚠️  No files were generated for {input_file.name}")
        
        # Handle watch mode after successful initial generation
        if watch and generated_files:
            if serve:
                # Start async watch mode with live server
                asyncio.run(_async_watch_with_serve(
                    input_file=input_file,
                    final_config=final_config,
                    output_dir=output_dir,
                    theme=theme,
                    template=template,
                    title=title,
                    author=author,
                    date=date,
                    institute=institute,
                    slides_only=slides_only,
                    notes_only=notes_only,
                    progress=progress,
                    ctx=ctx,
                    port=port,
                    auto_open=not no_open
                ))
            else:
                # Regular watch mode without server
                click.echo(f"\n👁️  Watch mode enabled. Monitoring {input_file} for changes...")
                click.echo("Press Ctrl+C to stop watching.")
                
                def regenerate_on_change(changed_file: Path) -> None:
                    """Callback function to regenerate files when input changes."""
                    # Only regenerate if the changed file is our input file
                    if changed_file.resolve() == input_file.resolve():
                        click.echo(f"\n🔄 Change detected in {changed_file.name}, regenerating...")
                        try:
                            # Re-run the generation process with the same parameters
                            # We'll call the internal generation logic directly
                            _perform_generation(
                                input_file=input_file,
                                final_config=final_config,
                                output_dir=output_dir,
                                theme=theme,
                                template=template,
                                title=title,
                                author=author,
                                date=date,
                                institute=institute,
                                slides_only=slides_only,
                                notes_only=notes_only,
                                overwrite=True,  # Always overwrite in watch mode
                                progress=progress,
                                ctx=ctx
                            )
                            click.echo(f"✓ Regeneration complete at {time.strftime('%H:%M:%S')}")
                        except Exception as e:
                            click.echo(f"✗ Error during regeneration: {e}", err=True)
                            logger.error(f"Watch mode regeneration error: {e}")
                
                try:
                    with create_file_watcher(regenerate_on_change, debounce_seconds=2.0) as watcher:
                        watcher.watch_file(input_file)
                        watcher.start()
                        watcher.wait()
                except KeyboardInterrupt:
                    click.echo(f"\n👋 Watch mode stopped.")
                except Exception as e:
                    click.echo(f"\n❌ Watch mode error: {e}", err=True)
                    logger.error(f"Watch mode error: {e}")
        
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        raise click.ClickException(str(e))
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
    help="Output directory for generated files. Default from config or ./output"
)
@click.option(
    '--pattern', '-p',
    help="File pattern to match. Default from config or *.md"
)
@click.option(
    '--recursive', '-r',
    is_flag=True,
    help="Process subdirectories recursively"
)
@click.option(
    '--format', '-f',
    multiple=True,
    type=click.Choice(['html', 'pdf', 'pptx', 'beamer'], case_sensitive=False),
    help="Output format(s). Default from config or html"
)
@click.option(
    '--theme', '-t',
    help="Theme for slides. Default from config"
)
@click.option(
    '--config', '-c',
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to YAML configuration file"
)
@click.option(
    '--parallel/--no-parallel',
    default=None,
    help="Enable parallel processing"
)
@click.option(
    '--max-workers',
    type=int,
    help="Maximum number of parallel workers"
)
@click.option(
    '--continue-on-error',
    is_flag=True,
    help="Continue processing other files if one fails"
)
@click.option(
    '--overwrite',
    is_flag=True,
    help="Overwrite existing output files"
)
@click.option(
    '--dry-run',
    is_flag=True,
    help="Show what would be processed without generating files"
)
@click.option(
    '--progress/--no-progress',
    default=True,
    help="Show progress indicators"
)
@click.pass_context
def batch(
    ctx,
    input_dir: Path,
    output_dir: Optional[Path],
    pattern: Optional[str],
    recursive: bool,
    format: List[str],
    theme: Optional[str],
    config: Optional[Path],
    parallel: Optional[bool],
    max_workers: Optional[int],
    continue_on_error: bool,
    overwrite: bool,
    dry_run: bool,
    progress: bool
):
    """
    Batch process multiple markdown files in a directory.
    
    INPUT_DIR: Directory containing markdown files to process.
    
    This command processes all matching markdown files in the specified directory,
    maintaining the directory structure in the output. Supports parallel processing
    and intelligent error handling.
    
    Examples:
    
        # Process all .md files in lectures directory
        markdown-slides batch lectures/
        
        # Process recursively with custom pattern and config
        markdown-slides batch content/ -r -p "lecture*.md" -c my-config.yaml
        
        # Generate multiple formats with parallel processing
        markdown-slides batch lectures/ -f html -f pdf --parallel --max-workers 4
        
        # Continue processing even if some files fail
        markdown-slides batch lectures/ --continue-on-error
    """
    try:
        # Load configuration
        try:
            base_config = config_manager.load_config(config)
        except ConfigurationError as e:
            raise click.ClickException(f"Configuration error: {e}")
        
        # Merge CLI options with configuration
        cli_options = {
            'format': format if format else None,
            'output_dir': str(output_dir) if output_dir else None,
            'theme': theme,
            'verbose': ctx.obj.get('verbose', False),
            'quiet': ctx.obj.get('quiet', False),
        }
        
        # Remove None values
        cli_options = {k: v for k, v in cli_options.items() if v is not None}
        
        # Merge configurations
        final_config = config_manager.merge_cli_options(base_config, cli_options)
        
        # Apply batch-specific overrides
        if pattern is not None:
            final_config.batch.pattern = pattern
        if recursive:
            final_config.batch.recursive = True
        if parallel is not None:
            final_config.batch.parallel = parallel
        if max_workers is not None:
            final_config.batch.max_workers = max_workers
        if continue_on_error:
            final_config.batch.error_handling = 'continue'
        if overwrite:
            final_config.output.overwrite = True
        
        # Apply defaults
        if not final_config.output.formats:
            final_config.output.formats = ['html']
        if not output_dir:
            output_dir = Path(final_config.output.directory)
        
        # Setup logging
        setup_logging(final_config.logging.level)
        
        logger.info(f"Batch processing directory: {input_dir}")
        logger.info(f"Pattern: {final_config.batch.pattern}")
        logger.info(f"Recursive: {final_config.batch.recursive}")
        logger.info(f"Parallel: {final_config.batch.parallel}")
        
        # Find matching files
        if final_config.batch.recursive:
            files = list(input_dir.rglob(final_config.batch.pattern))
        else:
            files = list(input_dir.glob(final_config.batch.pattern))
        
        # Apply exclude patterns
        if final_config.batch.exclude_patterns:
            original_count = len(files)
            for exclude_pattern in final_config.batch.exclude_patterns:
                files = [f for f in files if not f.match(exclude_pattern)]
            excluded_count = original_count - len(files)
            if excluded_count > 0:
                logger.info(f"Excluded {excluded_count} files based on exclude patterns")
        
        if not files:
            click.echo(f"No files matching '{final_config.batch.pattern}' found in {input_dir}")
            return
        
        if progress and not ctx.obj.get('quiet', False):
            click.echo(f"📁 Found {len(files)} file(s) to process:")
            for file in files[:10]:  # Show first 10 files
                click.echo(f"  • {file.relative_to(input_dir)}")
            if len(files) > 10:
                click.echo(f"  ... and {len(files) - 10} more files")
            click.echo()
        
        if dry_run:
            click.echo(f"[DRY RUN] Batch processing configuration:")
            click.echo(f"  Input directory: {input_dir}")
            click.echo(f"  Pattern: {final_config.batch.pattern}")
            click.echo(f"  Recursive: {final_config.batch.recursive}")
            click.echo(f"  Files found: {len(files)}")
            click.echo(f"  Output formats: {', '.join(final_config.output.formats)}")
            click.echo(f"  Output directory: {output_dir}")
            click.echo(f"  Parallel processing: {final_config.batch.parallel}")
            if final_config.batch.parallel:
                click.echo(f"  Max workers: {final_config.batch.max_workers}")
            click.echo(f"  Error handling: {final_config.batch.error_handling}")
            return
        
        # Initialize batch processor
        from .batch import BatchProcessor
        
        batch_processor = BatchProcessor(final_config)
        
        # Process files using batch processor
        try:
            batch_result = batch_processor.process_directory(
                input_dir=input_dir,
                output_dir=output_dir,
                dry_run=dry_run
            )
            
            # Summary
            click.echo(f"\n📊 Batch processing complete:")
            click.echo(f"  📁 Input directory: {input_dir}")
            click.echo(f"  📤 Output directory: {output_dir}")
            click.echo(f"  ✓ Successfully processed: {batch_result.successful_files}")
            if batch_result.skipped_files > 0:
                click.echo(f"  ⏭️  Skipped: {batch_result.skipped_files}")
            if batch_result.failed_files > 0:
                click.echo(f"  ✗ Errors: {batch_result.failed_files}")
            click.echo(f"  📄 Total files generated: {len(batch_result.generated_outputs)}")
            click.echo(f"  ⏱️  Processing time: {batch_result.processing_time:.2f}s")
            click.echo(f"  📈 Success rate: {batch_result.success_rate:.1f}%")
            
            # Show recent errors if any
            if batch_result.errors:
                click.echo(f"\n⚠️  Recent errors:")
                for error in batch_result.errors[-3:]:
                    click.echo(f"  • {Path(error['file']).name}: {error['error']}")
            
            if batch_result.failed_files > 0 and final_config.batch.error_handling == 'stop':
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise click.ClickException(f"Batch processing failed: {e}")
        
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        raise click.ClickException(str(e))
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
        
        # Show application built-in themes (comprehensive themes)
        if builtin_themes:
            click.echo("📚 Application Built-in Themes (Comprehensive Academic Themes):")
            click.echo("   Use these for rich academic presentations with custom styling")
            for name, info in builtin_themes.items():
                click.echo(f"  • {name}")
                click.echo(f"    {info['display_name']} - {info['description']}")
                click.echo(f"    Style: {info['style']}, Color: {info['color_scheme']}")
                click.echo()
        
        # Show RevealJS standard themes
        click.echo("🌈 RevealJS Standard Themes (Basic Color Schemes):")
        click.echo("   Use these for simple, standard RevealJS presentations")
        revealjs_themes = [
            ('white', 'Clean white background theme (default)'),
            ('black', 'Black background with white text'),
            ('league', 'Dark theme with orange accents'),
            ('beige', 'Beige background with brown text'),
            ('sky', 'Blue gradient background'),
            ('night', 'Dark blue background'),
            ('serif', 'Serif fonts with brown accents'),
            ('simple', 'Minimal black on white'),
            ('solarized', 'Solarized color scheme'),
            ('blood', 'Dark red/black theme'),
            ('moon', 'Dark theme with blue accents'),
            ('dracula', 'Dark purple theme')
        ]
        
        for theme_name, description in revealjs_themes:
            click.echo(f"  • {theme_name}")
            click.echo(f"    {description}")
        click.echo()
        
        # Show custom themes if any
        if custom_themes:
            click.echo("🔧 Custom Themes:")
            for name, info in custom_themes.items():
                click.echo(f"  • {name}")
                click.echo(f"    {info['display_name']} - {info['description']}")
                click.echo(f"    Style: {info['style']}, Color: {info['color_scheme']}")
                click.echo()
        else:
            click.echo("🔧 Custom Themes:")
            click.echo("   No custom themes found. Create one with 'create-theme' command.")
        
        # Usage instructions
        click.echo("\n📝 Usage:")
        click.echo("   • Built-in themes: markdown-slides generate file.md -t academic-minimal")
        click.echo("   • RevealJS themes: markdown-slides generate file.md -t solarized")
        click.echo("   • In config file:  theme: academic-minimal  or  theme: solarized")
        
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
@click.option(
    '--output', '-o',
    type=click.Path(path_type=Path),
    help="Output path for configuration file"
)
@click.option(
    '--template-type',
    type=click.Choice(['minimal', 'standard', 'advanced']),
    default='standard',
    help="Type of configuration template to generate"
)
def init_config(output: Optional[Path], template_type: str):
    """
    Initialize a new configuration file with default settings.
    
    Creates a YAML configuration file with sensible defaults that can be
    customized for your specific needs.
    
    Examples:
    
        # Create default config in current directory
        markdown-slides init-config
        
        # Create config with specific name
        markdown-slides init-config -o my-lectures.yaml
        
        # Create advanced config with all options
        markdown-slides init-config --template-type advanced
    """
    try:
        if not output:
            output = Path('markdown-slides-config.yaml')
        
        if output.exists():
            if not click.confirm(f"Configuration file {output} already exists. Overwrite?"):
                click.echo("Operation cancelled.")
                return
        
        # Create configuration based on template type
        if template_type == 'minimal':
            config = Config()
            config.name = 'minimal-config'
            config.description = 'Minimal configuration for basic usage'
        elif template_type == 'advanced':
            config = Config()
            config.name = 'advanced-config'
            config.description = 'Advanced configuration with all options'
            # Add advanced settings
            config.slides.auto_split = True
            config.slides.max_content_length = 800
            config.notes.include_toc = True
            config.notes.cross_references = True
            config.processing.syntax_highlighting = True
            config.processing.math_renderer = 'mathjax'
            config.batch.parallel = True
            config.batch.progress_reporting = True
            config.variables = {
                'author': 'Your Name',
                'institute': 'Your Institution',
                'course': 'Course Name'
            }
        else:  # standard
            config = Config()
            config.name = 'standard-config'
            config.description = 'Standard configuration for typical usage'
            config.variables = {
                'author': 'Your Name',
                'institute': 'Your Institution'
            }
        
        # Save configuration
        config_manager.save_config(config, output)
        
        click.echo(f"✓ Created {template_type} configuration: {output}")
        click.echo(f"📝 Edit the file to customize settings for your needs")
        click.echo(f"🚀 Use with: markdown-slides generate file.md -c {output}")
        
    except Exception as e:
        logger.error(f"Error creating configuration: {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.argument(
    'config_file',
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True
)
def validate_config(config_file: Path):
    """
    Validate a configuration file for errors and warnings.
    
    CONFIG_FILE: Path to the YAML configuration file to validate.
    
    Checks the configuration file for syntax errors, invalid values,
    and provides suggestions for improvements.
    
    Examples:
    
        # Validate configuration file
        markdown-slides validate-config my-config.yaml
    """
    try:
        click.echo(f"🔍 Validating configuration: {config_file}")
        
        # Load and validate configuration
        config = config_manager.load_config(config_file)
        
        click.echo("✓ Configuration is valid")
        click.echo(f"📋 Configuration summary:")
        click.echo(f"  Name: {config.name}")
        click.echo(f"  Description: {config.description}")
        click.echo(f"  Output formats: {', '.join(config.output.formats)}")
        click.echo(f"  Slides theme: {config.slides.theme}")
        click.echo(f"  Notes style: {config.notes.style}")
        
        if config.variables:
            click.echo(f"  Variables: {len(config.variables)} defined")
        
    except ConfigurationError as e:
        click.echo(f"✗ Configuration validation failed:")
        click.echo(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error validating configuration: {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.argument(
    'config_file',
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True
)
def show_config(config_file: Path):
    """
    Display the contents of a configuration file in a readable format.
    
    CONFIG_FILE: Path to the YAML configuration file to display.
    
    Shows the configuration in a formatted, easy-to-read manner with
    explanations of each section.
    
    Examples:
    
        # Show configuration contents
        markdown-slides show-config my-config.yaml
    """
    try:
        config = config_manager.load_config(config_file)
        
        click.echo(f"📄 Configuration: {config_file}")
        click.echo(f"{'=' * 50}")
        click.echo()
        
        click.echo(f"🏷️  Metadata:")
        click.echo(f"   Name: {config.name}")
        click.echo(f"   Description: {config.description}")
        click.echo(f"   Version: {config.version}")
        click.echo()
        
        click.echo(f"📤 Output Settings:")
        click.echo(f"   Formats: {', '.join(config.output.formats)}")
        click.echo(f"   Directory: {config.output.directory}")
        click.echo(f"   Preserve structure: {config.output.preserve_structure}")
        click.echo(f"   Overwrite: {config.output.overwrite}")
        click.echo()
        
        click.echo(f"🎨 Slides Settings:")
        click.echo(f"   Theme: {config.slides.theme}")
        click.echo(f"   Template: {config.slides.template or 'default'}")
        click.echo(f"   Auto split: {config.slides.auto_split}")
        click.echo(f"   Max content length: {config.slides.max_content_length}")
        click.echo(f"   Transition: {config.slides.transition}")
        click.echo()
        
        click.echo(f"📚 Notes Settings:")
        click.echo(f"   Style: {config.notes.style}")
        click.echo(f"   Template: {config.notes.template or 'default'}")
        click.echo(f"   Include TOC: {config.notes.include_toc}")
        click.echo(f"   Page numbers: {config.notes.page_numbers}")
        click.echo(f"   Cross references: {config.notes.cross_references}")
        click.echo()
        
        click.echo(f"⚙️  Processing Settings:")
        click.echo(f"   Math renderer: {config.processing.math_renderer}")
        click.echo(f"   Syntax highlighting: {config.processing.syntax_highlighting}")
        click.echo(f"   Intelligent splitting: {config.processing.intelligent_splitting}")
        click.echo()
        
        if config.variables:
            click.echo(f"🔧 Variables:")
            for key, value in config.variables.items():
                click.echo(f"   {key}: {value}")
            click.echo()
        
        click.echo(f"📦 Batch Processing:")
        click.echo(f"   Pattern: {config.batch.pattern}")
        click.echo(f"   Recursive: {config.batch.recursive}")
        click.echo(f"   Parallel: {config.batch.parallel}")
        click.echo(f"   Max workers: {config.batch.max_workers}")
        
    except Exception as e:
        logger.error(f"Error displaying configuration: {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.argument(
    'input_dir',
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True
)
@click.option(
    '--config', '-c',
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to YAML configuration file"
)
@click.option(
    '--pattern', '-p',
    help="File pattern to match. Default from config or *.md"
)
@click.option(
    '--recursive', '-r',
    is_flag=True,
    help="Process subdirectories recursively"
)
@click.pass_context
def estimate(ctx, input_dir: Path, config: Optional[Path], pattern: Optional[str], recursive: bool):
    """
    Estimate processing time and resources for batch processing.
    
    INPUT_DIR: Directory containing markdown files to analyze.
    
    Provides detailed estimates of processing time, output files, and resource
    requirements before running actual batch processing.
    
    Examples:
    
        # Get processing estimate for directory
        markdown-slides estimate lectures/
        
        # Estimate with custom configuration
        markdown-slides estimate lectures/ -c my-config.yaml
        
        # Estimate recursive processing
        markdown-slides estimate content/ -r
    """
    try:
        # Load configuration
        try:
            base_config = config_manager.load_config(config)
        except ConfigurationError as e:
            raise click.ClickException(f"Configuration error: {e}")
        
        # Apply CLI overrides
        if pattern is not None:
            base_config.batch.pattern = pattern
        if recursive:
            base_config.batch.recursive = True
        
        # Initialize batch processor
        from .batch import BatchProcessor
        
        batch_processor = BatchProcessor(base_config)
        
        # Get processing estimate
        estimate_data = batch_processor.get_processing_estimate(input_dir)
        
        if 'error' in estimate_data:
            click.echo(f"✗ Error calculating estimate: {estimate_data['error']}")
            return
        
        # Display estimate
        click.echo(f"📊 Processing Estimate for {input_dir}")
        click.echo(f"{'=' * 50}")
        click.echo()
        
        click.echo(f"📁 Files:")
        click.echo(f"   Total files found: {estimate_data['total_files']}")
        click.echo(f"   Pattern: {base_config.batch.pattern}")
        click.echo(f"   Recursive: {base_config.batch.recursive}")
        click.echo()
        
        if estimate_data['total_files'] > 0:
            click.echo(f"⏱️  Time Estimate:")
            click.echo(f"   Estimated processing time: {estimate_data['estimated_time_human']}")
            if estimate_data['parallel_processing']:
                parallel_time = estimate_data['estimated_time_seconds'] / estimate_data['max_workers']
                click.echo(f"   With parallel processing ({estimate_data['max_workers']} workers): {parallel_time/60:.1f} minutes")
            click.echo()
            
            click.echo(f"📤 Output:")
            click.echo(f"   Output formats: {', '.join(estimate_data['output_formats'])}")
            click.echo(f"   Estimated output files: {estimate_data['estimated_outputs']}")
            click.echo()
            
            click.echo(f"💾 Storage:")
            click.echo(f"   Total input size: {estimate_data['total_size_human']}")
            estimated_output_size = estimate_data['total_size_bytes'] * len(estimate_data['output_formats']) * 2
            click.echo(f"   Estimated output size: {batch_processor.file_scanner._format_file_size(estimated_output_size)}")
            click.echo()
            
            click.echo(f"⚙️  Processing:")
            click.echo(f"   Parallel processing: {estimate_data['parallel_processing']}")
            if estimate_data['parallel_processing']:
                click.echo(f"   Max workers: {estimate_data['max_workers']}")
            click.echo()
            
            # Recommendations
            click.echo(f"💡 Recommendations:")
            if estimate_data['total_files'] > 50 and not estimate_data['parallel_processing']:
                click.echo(f"   • Consider enabling parallel processing for faster execution")
            if estimate_data['estimated_time_seconds'] > 300:  # 5 minutes
                click.echo(f"   • Large batch - consider processing in smaller chunks")
            if estimated_output_size > 1024**3:  # 1GB
                click.echo(f"   • Large output expected - ensure sufficient disk space")
        else:
            click.echo("ℹ️  No files found matching the specified criteria")
        
    except Exception as e:
        logger.error(f"Error calculating estimate: {e}")
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
        
        # Check Python version
        import sys
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        click.echo(f"✓ Python {python_version}")
        
        # Check for Quarto
        import subprocess
        try:
            result = subprocess.run(['quarto', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                quarto_version = result.stdout.strip()
                click.echo(f"✓ Quarto {quarto_version}")
            else:
                click.echo("✗ Quarto not found or not working")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            click.echo("✗ Quarto not found in PATH")
        
        # Check for LaTeX (optional but recommended)
        try:
            result = subprocess.run(['pdflatex', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                click.echo("✓ LaTeX (pdflatex) available")
            else:
                click.echo("⚠️  LaTeX not found (PDF generation may not work)")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            click.echo("⚠️  LaTeX not found (PDF generation may not work)")
        
        # Check configuration directory
        config_dir = Path.home() / '.markdown-slides'
        if config_dir.exists():
            click.echo(f"✓ Configuration directory: {config_dir}")
        else:
            click.echo(f"ℹ️  Configuration directory not found: {config_dir}")
        
        click.echo("\n🎉 System check complete!")
        
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