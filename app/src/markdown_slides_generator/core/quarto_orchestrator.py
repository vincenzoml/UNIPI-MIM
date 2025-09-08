"""
Quarto Orchestrator - Professional Quarto command interface and configuration management.

Implements comprehensive Quarto command building with format-specific optimizations,
robust error handling, and advanced configuration management for academic presentations.
"""

import subprocess
import json
import re
import shutil
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import yaml

from ..utils.logger import get_logger
from ..utils.exceptions import handle_exception, OutputError
from ..themes.theme_manager import ThemeManager, AcademicTheme
from ..themes.template_manager import TemplateManager, TemplateConfig, TemplateType, OutputFormat as TemplateOutputFormat

logger = get_logger(__name__)


class OutputFormat(Enum):
    """Supported output formats with their Quarto format names."""
    REVEALJS = "revealjs"
    BEAMER = "beamer"
    PPTX = "pptx"
    PDF = "pdf"
    HTML = "html"


@dataclass
class QuartoCommand:
    """Represents a Quarto command with all its arguments."""
    input_file: str
    output_format: str
    output_file: Optional[str] = None
    args: List[str] = None
    env_vars: Dict[str, str] = None
    
    def __post_init__(self):
        if self.args is None:
            self.args = []
        if self.env_vars is None:
            self.env_vars = {}


@dataclass
class QuartoResult:
    """Result of a Quarto command execution."""
    success: bool
    output_file: Optional[str]
    stdout: str
    stderr: str
    return_code: int
    execution_time: float
    warnings: List[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []


class QuartoCommandBuilder:
    """
    Builds Quarto commands with format-specific optimizations.
    
    Handles all supported output formats with appropriate settings for
    academic presentations and lecture notes.
    """
    
    # Format-specific optimizations
    FORMAT_CONFIGS = {
        OutputFormat.REVEALJS: {
            'theme': 'white',
            'slide-number': True,
            'chalkboard': True,
            'preview-links': 'auto',
            'transition': 'slide',
            'background-transition': 'fade',
            'hash': True,
            'history': False,
            'controls': True,
            'progress': True,
            'center': True,
            'touch': True,
            'loop': False,
            'rtl': False,
            'navigation-mode': 'default',
            'keyboard': True,
            'overview': True,
            'disable-layout': False,
            'mouse-wheel': False,
            'hide-inactive-cursor': True,
            'hide-cursor-timeout': 5000,
            'help': True,
            'show-notes': False,
            'auto-animate': True,
            'auto-animate-easing': 'ease',
            'auto-animate-duration': 1.0,
            'auto-animate-unmatched': True,
            'menu': {
                'side': 'left',
                'width': 'normal',
                'numbers': False,
                'titleSelector': 'h1, h2, h3, h4, h5, h6',
                'useTextContentForMissingTitles': False,
                'hideMissingTitles': False,
                'markers': True,
                'custom': False,
                'themes': False,
                'themesPath': 'dist/theme/',
                'transitions': False,
                'openButton': True,
                'openSlideNumber': False,
                'keyboard': True,
                'sticky': False,
                'autoOpen': False,
                'delayInit': False,
                'openOnInit': False,
                'loadIcons': True
            }
        },
        OutputFormat.BEAMER: {
            'theme': 'Madrid',
            'colortheme': 'default',
            'fonttheme': 'default',
            'aspectratio': '169',  # 16:9 aspect ratio
            'navigation': 'horizontal',
            'pdf-engine': 'xelatex',
            'cite-method': 'biblatex'
        },
        OutputFormat.PPTX: {
            'slide-level': 2,
            'incremental': False,
            'reference-doc': None  # Can be set to custom template
        },
        OutputFormat.PDF: {
            'pdf-engine': 'xelatex',
            'documentclass': 'article',
            'geometry': 'margin=1in',
            'fontsize': '11pt',
            'linestretch': 1.2,
            'indent': True,
            'cite-method': 'biblatex',
            'keep-tex': False
        },
        OutputFormat.HTML: {
            'theme': 'cosmo',
            'toc': True,
            'toc-depth': 3,
            'number-sections': True,
            'highlight-style': 'github',
            'code-fold': False,
            'code-tools': True,
            'self-contained': False
        }
    }
    
    def __init__(self):
        self.custom_configs = {}
    
    def build_command(
        self, 
        input_file: str, 
        output_format: OutputFormat,
        output_file: Optional[str] = None,
        custom_config: Optional[Dict[str, Any]] = None,
        project_dir: Optional[str] = None
    ) -> QuartoCommand:
        """
        Build a Quarto command with format-specific optimizations.
        
        Args:
            input_file: Path to input .qmd file
            output_format: Target output format
            output_file: Optional custom output file path
            custom_config: Optional custom configuration overrides
            project_dir: Optional project directory for relative paths
            
        Returns:
            QuartoCommand object ready for execution
        """
        logger.debug(f"Building Quarto command for {output_format.value} format")
        
        # Start with base command
        args = ['quarto', 'render', input_file]
        
        # Add format specification
        args.extend(['--to', output_format.value])
        
        # Add output file if specified
        if output_file:
            args.extend(['--output', output_file])
        
        # Get format-specific configuration
        format_config = self.FORMAT_CONFIGS.get(output_format, {}).copy()
        
        # Apply custom configuration overrides
        if custom_config:
            format_config.update(custom_config)
        
        # Convert configuration to command line arguments
        format_args = self._config_to_args(format_config, output_format)
        args.extend(format_args)
        
        # Set up environment variables
        env_vars = {}
        
        # Add project directory to environment if specified
        if project_dir:
            env_vars['QUARTO_PROJECT_DIR'] = project_dir
        
        return QuartoCommand(
            input_file=input_file,
            output_format=output_format.value,
            output_file=output_file,
            args=args,
            env_vars=env_vars
        )
    
    def _config_to_args(self, config: Dict[str, Any], format_type: OutputFormat) -> List[str]:
        """
        Convert configuration dictionary to command line arguments.
        
        Args:
            config: Configuration dictionary
            format_type: Output format type for format-specific handling
            
        Returns:
            List of command line arguments
        """
        args = []
        
        for key, value in config.items():
            if value is None:
                continue
                
            # Handle different value types
            if isinstance(value, bool):
                if value:
                    args.extend([f'--{key}'])
            elif isinstance(value, (str, int, float)):
                args.extend([f'--{key}', str(value)])
            elif isinstance(value, dict):
                # For nested configurations, we'll handle them in YAML frontmatter
                # This is more appropriate for complex Quarto configurations
                continue
            elif isinstance(value, list):
                # Handle list values (e.g., for multiple options)
                for item in value:
                    args.extend([f'--{key}', str(item)])
        
        return args
    
    def build_slides_command(
        self,
        input_file: str,
        format: str = "revealjs",
        theme: str = "white",
        output_file: Optional[str] = None,
        custom_options: Optional[Dict[str, Any]] = None
    ) -> QuartoCommand:
        """
        Build optimized command for slide generation.
        
        Args:
            input_file: Path to slides .qmd file
            format: Output format (revealjs, beamer, pptx)
            theme: Presentation theme
            output_file: Optional output file path
            custom_options: Optional custom configuration
            
        Returns:
            QuartoCommand for slide generation
        """
        # Map string format to enum
        format_enum = OutputFormat(format.lower())
        
        # Prepare slide-specific configuration
        slide_config = {'theme': theme}
        if custom_options:
            slide_config.update(custom_options)
        
        return self.build_command(
            input_file=input_file,
            output_format=format_enum,
            output_file=output_file,
            custom_config=slide_config
        )
    
    def build_notes_command(
        self,
        input_file: str,
        format: str = "pdf",
        output_file: Optional[str] = None,
        academic_style: bool = True,
        custom_options: Optional[Dict[str, Any]] = None
    ) -> QuartoCommand:
        """
        Build optimized command for notes generation.
        
        Args:
            input_file: Path to notes .qmd file
            format: Output format (pdf, html)
            output_file: Optional output file path
            academic_style: Whether to use academic formatting
            custom_options: Optional custom configuration
            
        Returns:
            QuartoCommand for notes generation
        """
        # Map string format to enum
        format_enum = OutputFormat(format.lower())
        
        # Prepare notes-specific configuration
        notes_config = {}
        
        if academic_style and format_enum == OutputFormat.PDF:
            notes_config.update({
                'documentclass': 'article',
                'geometry': 'margin=1in',
                'fontsize': '11pt',
                'linestretch': 1.2,
                'toc': True,
                'number-sections': True,
                'cite-method': 'biblatex'
            })
        elif academic_style and format_enum == OutputFormat.HTML:
            notes_config.update({
                'theme': 'cosmo',
                'toc': True,
                'toc-depth': 3,
                'number-sections': True,
                'code-fold': True
            })
        
        if custom_options:
            notes_config.update(custom_options)
        
        return self.build_command(
            input_file=input_file,
            output_format=format_enum,
            output_file=output_file,
            custom_config=notes_config
        )


class QuartoExecutor:
    """
    Executes Quarto commands with robust error handling and output parsing.
    
    Provides comprehensive error reporting, progress tracking, and result analysis
    for all Quarto operations.
    """
    
    def __init__(self):
        self.last_result: Optional[QuartoResult] = None
        self._check_quarto_installation()
    
    def _check_quarto_installation(self) -> bool:
        """
        Check if Quarto is installed and accessible.
        
        Returns:
            True if Quarto is available, False otherwise
            
        Raises:
            OutputError: If Quarto is not found or not working
        """
        try:
            result = subprocess.run(
                ['quarto', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"Quarto version: {version}")
                return True
            else:
                raise OutputError(f"Quarto check failed: {result.stderr}")
                
        except FileNotFoundError:
            raise OutputError(
                "Quarto not found. Please install Quarto from https://quarto.org/docs/get-started/installation.html"
            )
        except subprocess.TimeoutExpired:
            raise OutputError("Quarto version check timed out")
        except Exception as e:
            raise OutputError(f"Error checking Quarto installation: {e}")
    
    @handle_exception
    def execute_command(self, command: QuartoCommand, timeout: int = 300) -> QuartoResult:
        """
        Execute a Quarto command with comprehensive error handling.
        
        Args:
            command: QuartoCommand to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            QuartoResult with execution details and results
            
        Raises:
            OutputError: If command execution fails critically
        """
        import time
        start_time = time.time()
        
        logger.info(f"Executing Quarto command: {' '.join(command.args)}")
        logger.debug(f"Input file: {command.input_file}")
        logger.debug(f"Output format: {command.output_format}")
        
        try:
            # Prepare environment
            env = dict(os.environ)
            env.update(command.env_vars)
            
            # Execute command
            result = subprocess.run(
                command.args,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                cwd=Path(command.input_file).parent if Path(command.input_file).exists() else None
            )
            
            execution_time = time.time() - start_time
            
            # Parse output and errors
            warnings, errors = self._parse_quarto_output(result.stdout, result.stderr)
            
            # Determine success
            success = result.returncode == 0 and not errors
            
            # Find output file
            output_file = self._find_output_file(command, result.stdout)
            
            quarto_result = QuartoResult(
                success=success,
                output_file=output_file,
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode,
                execution_time=execution_time,
                warnings=warnings,
                errors=errors
            )
            
            self.last_result = quarto_result
            
            if success:
                logger.info(f"Quarto command completed successfully in {execution_time:.2f}s")
                if output_file:
                    logger.info(f"Generated output: {output_file}")
            else:
                logger.error(f"Quarto command failed with return code {result.returncode}")
                for error in errors:
                    logger.error(f"Error: {error}")
            
            # Log warnings
            for warning in warnings:
                logger.warning(f"Warning: {warning}")
            
            return quarto_result
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            error_msg = f"Quarto command timed out after {timeout} seconds"
            logger.error(error_msg)
            
            return QuartoResult(
                success=False,
                output_file=None,
                stdout="",
                stderr=error_msg,
                return_code=-1,
                execution_time=execution_time,
                errors=[error_msg]
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error executing Quarto command: {e}"
            logger.error(error_msg)
            
            return QuartoResult(
                success=False,
                output_file=None,
                stdout="",
                stderr=str(e),
                return_code=-1,
                execution_time=execution_time,
                errors=[error_msg]
            )
    
    def _parse_quarto_output(self, stdout: str, stderr: str) -> Tuple[List[str], List[str]]:
        """
        Parse Quarto output to extract warnings and errors.
        
        Args:
            stdout: Standard output from Quarto
            stderr: Standard error from Quarto
            
        Returns:
            Tuple of (warnings, errors)
        """
        warnings = []
        errors = []
        
        # Combine stdout and stderr for parsing
        combined_output = stdout + "\n" + stderr
        
        # Common Quarto warning patterns
        warning_patterns = [
            r'WARNING:.*',
            r'Warning:.*',
            r'\[WARNING\].*',
            r'.*warning:.*',
        ]
        
        # Common Quarto error patterns
        error_patterns = [
            r'ERROR:.*',
            r'Error:.*',
            r'\[ERROR\].*',
            r'.*error:.*',
            r'FATAL:.*',
            r'Fatal:.*',
            r'.*failed.*',
            r'.*not found.*',
            r'.*cannot.*',
        ]
        
        lines = combined_output.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for warnings
            for pattern in warning_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    warnings.append(line)
                    break
            else:
                # Check for errors (only if not already matched as warning)
                for pattern in error_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        errors.append(line)
                        break
        
        return warnings, errors
    
    def _find_output_file(self, command: QuartoCommand, stdout: str) -> Optional[str]:
        """
        Find the generated output file from command and stdout.
        
        Args:
            command: Original QuartoCommand
            stdout: Standard output from Quarto
            
        Returns:
            Path to output file if found, None otherwise
        """
        # If output file was explicitly specified
        if command.output_file:
            output_path = Path(command.output_file)
            if output_path.exists():
                return str(output_path.absolute())
        
        # Try to parse output file from stdout
        output_patterns = [
            r'Output created: (.+)',
            r'Generated: (.+)',
            r'Created: (.+)',
            r'Writing (.+)',
        ]
        
        for pattern in output_patterns:
            match = re.search(pattern, stdout)
            if match:
                output_file = match.group(1).strip()
                output_path = Path(output_file)
                if output_path.exists():
                    return str(output_path.absolute())
        
        # Try to infer output file based on input and format
        input_path = Path(command.input_file)
        if input_path.exists():
            base_name = input_path.stem
            parent_dir = input_path.parent
            
            # Common output extensions by format
            format_extensions = {
                'revealjs': '.html',
                'html': '.html',
                'beamer': '.pdf',
                'pdf': '.pdf',
                'pptx': '.pptx'
            }
            
            ext = format_extensions.get(command.output_format, '.html')
            potential_output = parent_dir / f"{base_name}{ext}"
            
            if potential_output.exists():
                return str(potential_output.absolute())
        
        return None


class QuartoOrchestrator:
    """
    Professional Quarto orchestration system with comprehensive command interface.
    
    Provides high-level interface for generating slides and notes using Quarto
    with format-specific optimizations and robust error handling.
    """
    
    def __init__(self):
        self.command_builder = QuartoCommandBuilder()
        self.executor = QuartoExecutor()
        self.last_results: Dict[str, QuartoResult] = {}
        
        # Initialize theme and template managers
        self.theme_manager = ThemeManager()
        self.template_manager = TemplateManager()
    
    @handle_exception
    def generate_slides(
        self, 
        input_file: str, 
        format: str = "revealjs",
        output_file: Optional[str] = None,
        theme: str = "white",
        custom_options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate slides from Quarto markdown file.
        
        Args:
            input_file: Path to .qmd file
            format: Output format (revealjs, beamer, pptx)
            output_file: Optional output file path
            theme: Presentation theme
            custom_options: Optional custom configuration
            
        Returns:
            Path to generated slides file
            
        Raises:
            OutputError: If slide generation fails
        """
        logger.info(f"Generating {format} slides from {input_file}")
        
        # Validate input file
        input_path = Path(input_file)
        if not input_path.exists():
            raise OutputError(f"Input file not found: {input_file}")
        
        # Build command
        command = self.command_builder.build_slides_command(
            input_file=input_file,
            format=format,
            theme=theme,
            output_file=output_file,
            custom_options=custom_options
        )
        
        # Execute command
        result = self.executor.execute_command(command)
        self.last_results[f"slides_{format}"] = result
        
        if not result.success:
            error_msg = f"Failed to generate {format} slides"
            if result.errors:
                error_msg += f": {'; '.join(result.errors)}"
            raise OutputError(error_msg)
        
        if not result.output_file:
            raise OutputError(f"No output file generated for {format} slides")
        
        logger.info(f"Successfully generated {format} slides: {result.output_file}")
        return result.output_file
    
    @handle_exception
    def generate_notes(
        self, 
        input_file: str, 
        format: str = "pdf",
        output_file: Optional[str] = None,
        academic_style: bool = True,
        custom_options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate notes from Quarto markdown file.
        
        Args:
            input_file: Path to .qmd file
            format: Output format (pdf, html)
            output_file: Optional output file path
            academic_style: Whether to use academic formatting
            custom_options: Optional custom configuration
            
        Returns:
            Path to generated notes file
            
        Raises:
            OutputError: If notes generation fails
        """
        logger.info(f"Generating {format} notes from {input_file}")
        
        # Validate input file
        input_path = Path(input_file)
        if not input_path.exists():
            raise OutputError(f"Input file not found: {input_file}")
        
        # Build command
        command = self.command_builder.build_notes_command(
            input_file=input_file,
            format=format,
            output_file=output_file,
            academic_style=academic_style,
            custom_options=custom_options
        )
        
        # Execute command
        result = self.executor.execute_command(command)
        self.last_results[f"notes_{format}"] = result
        
        if not result.success:
            error_msg = f"Failed to generate {format} notes"
            if result.errors:
                error_msg += f": {'; '.join(result.errors)}"
            raise OutputError(error_msg)
        
        if not result.output_file:
            raise OutputError(f"No output file generated for {format} notes")
        
        logger.info(f"Successfully generated {format} notes: {result.output_file}")
        return result.output_file
    
    @handle_exception
    def generate_themed_slides(
        self,
        input_file: str,
        theme_name: str = "academic-minimal",
        template_name: Optional[str] = None,
        format: str = "revealjs",
        output_file: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        custom_options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate slides with custom theme and template.
        
        Args:
            input_file: Path to .qmd file
            theme_name: Name of theme to use
            template_name: Optional template name
            format: Output format (revealjs, beamer, pptx)
            output_file: Optional output file path
            variables: Template variables
            custom_options: Optional custom configuration
            
        Returns:
            Path to generated slides file
            
        Raises:
            OutputError: If generation fails
        """
        logger.info(f"Generating themed slides with theme '{theme_name}' from {input_file}")
        
        # Get theme
        theme = self.theme_manager.get_theme(theme_name)
        
        # Prepare theme-specific options
        theme_options = {
            'theme': theme_name,
            'transition': theme.transition,
            'background-transition': theme.background_transition,
            'slide-number': theme.show_slide_numbers,
            'progress': theme.show_progress,
            'chalkboard': theme.enable_chalkboard,
            'menu': theme.enable_menu,
            'overview': theme.enable_overview
        }
        
        # Merge with custom options
        if custom_options:
            theme_options.update(custom_options)
        
        # Generate theme CSS if needed
        if theme_name.startswith('academic-'):
            css_content = self.theme_manager.generate_reveal_css(theme)
            css_file = Path(input_file).parent / f"{theme_name}.css"
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(css_content)
            theme_options['theme'] = str(css_file)
        
        # Use template if specified
        if template_name:
            template_config = self.template_manager.get_template(template_name)
            
            # Prepare template variables
            template_vars = variables or {}
            template_vars.update({
                'title': template_vars.get('title', 'Presentation'),
                'theme': theme_name
            })
            
            # Render template
            rendered_content = self.template_manager.render_template(
                template_name, input_file, template_vars
            )
            
            # Write rendered content to temporary file
            input_path = Path(input_file)
            temp_file = input_path.parent / f"temp_{input_path.stem}.qmd"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(rendered_content)
            
            try:
                # Generate slides from templated content
                result_file = self.generate_slides(
                    str(temp_file), format, output_file, theme_name, theme_options
                )
                return result_file
            finally:
                # Clean up temporary file
                if temp_file.exists():
                    temp_file.unlink()
        else:
            # Generate slides without template
            return self.generate_slides(
                input_file, format, output_file, theme_name, theme_options
            )
    
    @handle_exception
    def generate_templated_notes(
        self,
        input_file: str,
        template_name: Optional[str] = None,
        format: str = "pdf",
        output_file: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        academic_style: bool = True,
        custom_options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate notes with custom template.
        
        Args:
            input_file: Path to .qmd file
            template_name: Optional template name
            format: Output format (pdf, html)
            output_file: Optional output file path
            variables: Template variables
            academic_style: Whether to use academic formatting
            custom_options: Optional custom configuration
            
        Returns:
            Path to generated notes file
            
        Raises:
            OutputError: If generation fails
        """
        logger.info(f"Generating templated notes from {input_file}")
        
        # Use template if specified
        if template_name:
            template_config = self.template_manager.get_template(template_name)
            
            # Read original content
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prepare template variables
            template_vars = variables or {}
            template_vars.update({
                'title': template_vars.get('title', 'Lecture Notes')
            })
            
            # Render template
            rendered_content = self.template_manager.render_template(
                template_name, content, template_vars, include_title_slide=False
            )
            
            # Write rendered content to temporary file
            temp_file = Path(input_file).parent / f"temp_{Path(input_file).name}"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(rendered_content)
            
            try:
                # Generate notes from templated content
                result_file = self.generate_notes(
                    str(temp_file), format, output_file, academic_style, custom_options
                )
                return result_file
            finally:
                # Clean up temporary file
                if temp_file.exists():
                    temp_file.unlink()
        else:
            # Generate notes without template
            return self.generate_notes(
                input_file, format, output_file, academic_style, custom_options
            )
    
    def list_available_themes(self) -> Dict[str, Dict[str, str]]:
        """
        List all available themes.
        
        Returns:
            Dictionary with theme information
        """
        return self.theme_manager.list_themes()
    
    def list_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available templates.
        
        Returns:
            Dictionary with template information
        """
        return self.template_manager.list_templates()
    
    @handle_exception
    def create_custom_theme(
        self,
        name: str,
        base_theme: str = "academic-minimal",
        customizations: Optional[Dict[str, Any]] = None
    ) -> AcademicTheme:
        """
        Create a custom theme.
        
        Args:
            name: Name for the new theme
            base_theme: Base theme to customize
            customizations: Dictionary of customizations
            
        Returns:
            New AcademicTheme object
        """
        return self.theme_manager.create_custom_theme(name, base_theme, customizations)
    
    @handle_exception
    def create_custom_template(
        self,
        name: str,
        template_type: str,
        output_format: str,
        base_template: Optional[str] = None,
        customizations: Optional[Dict[str, Any]] = None
    ) -> TemplateConfig:
        """
        Create a custom template.
        
        Args:
            name: Name for the new template
            template_type: Type of template (slides, notes, handouts)
            output_format: Output format (revealjs, pdf, html, etc.)
            base_template: Optional base template to inherit from
            customizations: Optional customizations
            
        Returns:
            New TemplateConfig object
        """
        # Convert string enums
        template_type_enum = TemplateType(template_type.lower())
        output_format_enum = TemplateOutputFormat(output_format.lower())
        
        return self.template_manager.create_custom_template(
            name, template_type_enum, output_format_enum, base_template, customizations
        )
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        Get list of supported output formats.
        
        Returns:
            Dictionary with slides and notes format lists
        """
        return {
            'slides': ['revealjs', 'beamer', 'pptx'],
            'notes': ['pdf', 'html']
        }
    
    def get_last_result(self, result_type: str) -> Optional[QuartoResult]:
        """
        Get the last execution result for a specific type.
        
        Args:
            result_type: Type of result (e.g., 'slides_revealjs', 'notes_pdf')
            
        Returns:
            QuartoResult if available, None otherwise
        """
        return self.last_results.get(result_type)
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get summary of all recent executions.
        
        Returns:
            Dictionary with execution statistics and results
        """
        summary = {
            'total_executions': len(self.last_results),
            'successful': 0,
            'failed': 0,
            'total_time': 0.0,
            'results': {}
        }
        
        for result_type, result in self.last_results.items():
            summary['results'][result_type] = {
                'success': result.success,
                'execution_time': result.execution_time,
                'output_file': result.output_file,
                'warnings': len(result.warnings),
                'errors': len(result.errors)
            }
            
            if result.success:
                summary['successful'] += 1
            else:
                summary['failed'] += 1
            
            summary['total_time'] += result.execution_time
        
        return summary
    
    def create_quarto_config(self, config: Dict[str, Any]) -> str:
        """
        Create comprehensive Quarto configuration YAML.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            YAML configuration string
        """
        logger.debug("Creating comprehensive Quarto configuration")
        
        # Use the configuration manager for advanced config generation
        config_manager = QuartoConfigurationManager()
        
        # Generate appropriate configuration based on content type
        if 'slides' in config:
            slides_config = config_manager.create_slides_config(
                title=config.get('title', 'Presentation'),
                format_type=config.get('format', 'revealjs'),
                theme=config.get('theme', 'white'),
                custom_options=config.get('custom_options'),
                author=config.get('author'),
                date=config.get('date'),
                institute=config.get('institute')
            )
            return config_manager.generate_yaml_frontmatter(slides_config)
        
        elif 'notes' in config:
            notes_config = config_manager.create_notes_config(
                title=config.get('title', 'Lecture Notes'),
                format_type=config.get('format', 'pdf'),
                academic_style=config.get('academic_style', True),
                custom_options=config.get('custom_options'),
                author=config.get('author'),
                date=config.get('date'),
                bibliography=config.get('bibliography')
            )
            return config_manager.generate_yaml_frontmatter(notes_config)
        
        else:
            # Generic configuration
            quarto_config = {
                'project': {
                    'type': 'default'
                },
                'format': config.get('format', {})
            }
            return yaml.dump(quarto_config, default_flow_style=False)
    
    def create_project(
        self,
        project_name: str,
        project_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create a new Quarto project with proper structure.
        
        Args:
            project_name: Name of the project
            project_dir: Directory to create project in
            
        Returns:
            Dictionary with created file paths
        """
        logger.info(f"Creating new Quarto project: {project_name}")
        
        config_manager = QuartoConfigurationManager(project_dir)
        return config_manager.create_project_structure(project_name)
    
    def get_theme_manager(self) -> ThemeManager:
        """
        Get the theme manager instance.
        
        Returns:
            ThemeManager instance
        """
        return self.theme_manager
    
    def get_template_manager(self) -> TemplateManager:
        """
        Get the template manager instance.
        
        Returns:
            TemplateManager instance
        """
        return self.template_manager
    
    def get_configuration_manager(self, project_dir: Optional[str] = None) -> 'QuartoConfigurationManager':
        """
        Get the configuration manager instance.
        
        Args:
            project_dir: Optional project directory
            
        Returns:
            QuartoConfigurationManager instance
        """
        return QuartoConfigurationManager(project_dir)


class QuartoThemeManager:
    """
    Advanced theme selection and customization system for Quarto.
    
    Manages built-in themes, custom themes, and theme customizations
    for different output formats.
    """
    
    # Built-in themes for different formats
    BUILTIN_THEMES = {
        'revealjs': [
            'beige', 'black', 'blood', 'league', 'moon', 'night',
            'serif', 'simple', 'sky', 'solarized', 'white'
        ],
        'beamer': [
            'default', 'AnnArbor', 'Antibes', 'Bergen', 'Berkeley',
            'Berlin', 'Boadilla', 'CambridgeUS', 'Copenhagen', 'Darmstadt',
            'Dresden', 'Frankfurt', 'Goettingen', 'Hannover', 'Ilmenau',
            'JuanLesPins', 'Luebeck', 'Madrid', 'Malmoe', 'Marburg',
            'Montpellier', 'PaloAlto', 'Pittsburgh', 'Rochester', 'Singapore',
            'Szeged', 'Warsaw'
        ],
        'html': [
            'bootstrap', 'cerulean', 'cosmo', 'darkly', 'flatly',
            'journal', 'litera', 'lumen', 'lux', 'materia',
            'minty', 'morph', 'pulse', 'quartz', 'sandstone',
            'simplex', 'sketchy', 'slate', 'solar', 'spacelab',
            'superhero', 'united', 'vapor', 'yeti', 'zephyr'
        ]
    }
    
    def __init__(self, custom_themes_dir: Optional[str] = None):
        self.custom_themes_dir = Path(custom_themes_dir) if custom_themes_dir else None
        self.theme_customizations = {}
    
    def get_available_themes(self, format_type: str) -> List[str]:
        """
        Get list of available themes for a specific format.
        
        Args:
            format_type: Output format (revealjs, beamer, html)
            
        Returns:
            List of available theme names
        """
        builtin = self.BUILTIN_THEMES.get(format_type, [])
        custom = self._get_custom_themes(format_type)
        return builtin + custom
    
    def _get_custom_themes(self, format_type: str) -> List[str]:
        """Get custom themes for a specific format."""
        if not self.custom_themes_dir or not self.custom_themes_dir.exists():
            return []
        
        theme_dir = self.custom_themes_dir / format_type
        if not theme_dir.exists():
            return []
        
        # Look for theme files (CSS for revealjs/html, sty for beamer)
        if format_type in ['revealjs', 'html']:
            theme_files = list(theme_dir.glob('*.css'))
        elif format_type == 'beamer':
            theme_files = list(theme_dir.glob('*.sty'))
        else:
            theme_files = []
        
        return [f.stem for f in theme_files]
    
    def validate_theme(self, theme_name: str, format_type: str) -> bool:
        """
        Validate that a theme exists for the given format.
        
        Args:
            theme_name: Name of the theme
            format_type: Output format
            
        Returns:
            True if theme is valid, False otherwise
        """
        available_themes = self.get_available_themes(format_type)
        return theme_name in available_themes
    
    def get_theme_path(self, theme_name: str, format_type: str) -> Optional[str]:
        """
        Get the path to a custom theme file.
        
        Args:
            theme_name: Name of the theme
            format_type: Output format
            
        Returns:
            Path to theme file if custom theme, None if built-in
        """
        if theme_name in self.BUILTIN_THEMES.get(format_type, []):
            return None  # Built-in theme
        
        if not self.custom_themes_dir:
            return None
        
        theme_dir = self.custom_themes_dir / format_type
        
        if format_type in ['revealjs', 'html']:
            theme_file = theme_dir / f"{theme_name}.css"
        elif format_type == 'beamer':
            theme_file = theme_dir / f"{theme_name}.sty"
        else:
            return None
        
        return str(theme_file) if theme_file.exists() else None
    
    def create_theme_customization(
        self,
        base_theme: str,
        customizations: Dict[str, Any],
        format_type: str
    ) -> Dict[str, Any]:
        """
        Create theme customization configuration.
        
        Args:
            base_theme: Base theme to customize
            customizations: Customization options
            format_type: Output format
            
        Returns:
            Theme configuration dictionary
        """
        theme_config = {'theme': base_theme}
        
        if format_type == 'revealjs':
            # RevealJS-specific customizations
            if 'colors' in customizations:
                theme_config.update(customizations['colors'])
            if 'fonts' in customizations:
                theme_config.update(customizations['fonts'])
            if 'layout' in customizations:
                theme_config.update(customizations['layout'])
                
        elif format_type == 'beamer':
            # Beamer-specific customizations
            if 'colortheme' in customizations:
                theme_config['colortheme'] = customizations['colortheme']
            if 'fonttheme' in customizations:
                theme_config['fonttheme'] = customizations['fonttheme']
            if 'innertheme' in customizations:
                theme_config['innertheme'] = customizations['innertheme']
            if 'outertheme' in customizations:
                theme_config['outertheme'] = customizations['outertheme']
                
        elif format_type == 'html':
            # HTML-specific customizations
            if 'css' in customizations:
                theme_config['css'] = customizations['css']
            if 'scss' in customizations:
                theme_config['scss'] = customizations['scss']
        
        return theme_config


class QuartoConfigurationManager:
    """
    Advanced Quarto configuration management system.
    
    Handles dynamic YAML configuration generation, project structure management,
    and template customization for academic presentations.
    """
    
    def __init__(self, project_dir: Optional[str] = None):
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.theme_manager = QuartoThemeManager()
        self.templates_dir = self.project_dir / "_templates"
        self.config_cache = {}
    
    def create_slides_config(
        self,
        title: str,
        format_type: str = "revealjs",
        theme: str = "white",
        custom_options: Optional[Dict[str, Any]] = None,
        author: Optional[str] = None,
        date: Optional[str] = None,
        institute: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive slides configuration.
        
        Args:
            title: Presentation title
            format_type: Output format (revealjs, beamer, pptx)
            theme: Theme name
            custom_options: Additional customization options
            author: Author name
            date: Presentation date
            institute: Institution name
            
        Returns:
            Complete slides configuration dictionary
        """
        logger.debug(f"Creating {format_type} slides configuration")
        
        # Base configuration
        config = {
            'title': title,
            'format': {}
        }
        
        # Add metadata if provided
        if author:
            config['author'] = author
        if date:
            config['date'] = date
        if institute:
            config['institute'] = institute
        
        # Format-specific configuration
        format_config = self._get_format_config(format_type, theme, custom_options)
        config['format'][format_type] = format_config
        
        # Add common settings
        config.update(self._get_common_settings())
        
        return config
    
    def create_notes_config(
        self,
        title: str,
        format_type: str = "pdf",
        academic_style: bool = True,
        custom_options: Optional[Dict[str, Any]] = None,
        author: Optional[str] = None,
        date: Optional[str] = None,
        bibliography: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive notes configuration.
        
        Args:
            title: Document title
            format_type: Output format (pdf, html)
            academic_style: Whether to use academic formatting
            custom_options: Additional customization options
            author: Author name
            date: Document date
            bibliography: Bibliography file path
            
        Returns:
            Complete notes configuration dictionary
        """
        logger.debug(f"Creating {format_type} notes configuration")
        
        # Base configuration
        config = {
            'title': title,
            'format': {}
        }
        
        # Add metadata if provided
        if author:
            config['author'] = author
        if date:
            config['date'] = date
        if bibliography:
            config['bibliography'] = bibliography
        
        # Format-specific configuration
        if academic_style:
            format_config = self._get_academic_format_config(format_type, custom_options)
        else:
            format_config = self._get_format_config(format_type, None, custom_options)
        
        config['format'][format_type] = format_config
        
        # Add common settings
        config.update(self._get_common_settings())
        
        return config
    
    def _get_format_config(
        self,
        format_type: str,
        theme: Optional[str] = None,
        custom_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get format-specific configuration."""
        # Start with default configuration from command builder
        base_config = QuartoCommandBuilder.FORMAT_CONFIGS.get(
            OutputFormat(format_type), {}
        ).copy()
        
        # Apply theme if specified
        if theme and self.theme_manager.validate_theme(theme, format_type):
            theme_config = self.theme_manager.create_theme_customization(
                theme, custom_options or {}, format_type
            )
            base_config.update(theme_config)
        
        # Apply custom options
        if custom_options:
            base_config.update(custom_options)
        
        return base_config
    
    def _get_academic_format_config(
        self,
        format_type: str,
        custom_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get academic-style format configuration."""
        if format_type == "pdf":
            config = {
                'documentclass': 'article',
                'geometry': 'margin=1in',
                'fontsize': '11pt',
                'linestretch': 1.2,
                'indent': True,
                'toc': True,
                'toc-depth': 3,
                'number-sections': True,
                'colorlinks': True,
                'pdf-engine': 'xelatex',
                'cite-method': 'biblatex',
                'keep-tex': False,
                'include-in-header': self._get_latex_header_includes()
            }
        elif format_type == "html":
            config = {
                'theme': 'cosmo',
                'toc': True,
                'toc-depth': 3,
                'toc-location': 'left',
                'number-sections': True,
                'number-depth': 3,
                'highlight-style': 'github',
                'code-fold': True,
                'code-tools': True,
                'code-copy': True,
                'self-contained': False,
                'anchor-sections': True,
                'smooth-scroll': True,
                'citations-hover': True,
                'crossrefs-hover': True
            }
        else:
            config = {}
        
        # Apply custom options
        if custom_options:
            config.update(custom_options)
        
        return config
    
    def _get_common_settings(self) -> Dict[str, Any]:
        """Get common settings for all documents."""
        return {
            'editor': 'visual',
            'execute': {
                'echo': True,
                'warning': True,
                'error': True,
                'cache': False
            },
            'lang': 'en'
        }
    
    def _get_latex_header_includes(self) -> List[str]:
        """Get LaTeX header includes for academic formatting."""
        includes = []
        
        # Check for custom header file
        header_file = self.templates_dir / "header.tex"
        if header_file.exists():
            includes.append(str(header_file))
        else:
            # Default academic packages
            includes.extend([
                "\\usepackage{amsmath,amssymb,amsfonts}",
                "\\usepackage{graphicx}",
                "\\usepackage{booktabs}",
                "\\usepackage{longtable}",
                "\\usepackage{array}",
                "\\usepackage{multirow}",
                "\\usepackage{wrapfig}",
                "\\usepackage{float}",
                "\\usepackage{colortbl}",
                "\\usepackage{pdflscape}",
                "\\usepackage{tabu}",
                "\\usepackage{threeparttable}",
                "\\usepackage{threeparttablex}",
                "\\usepackage[normalem]{ulem}",
                "\\usepackage{makecell}",
                "\\usepackage{xcolor}"
            ])
        
        return includes
    
    def create_project_structure(self, project_name: str) -> Dict[str, str]:
        """
        Create Quarto project structure with necessary directories and files.
        
        Args:
            project_name: Name of the project
            
        Returns:
            Dictionary mapping file types to their paths
        """
        logger.info(f"Creating Quarto project structure for {project_name}")
        
        project_path = self.project_dir / project_name
        project_path.mkdir(exist_ok=True)
        
        # Create directory structure
        directories = {
            'slides': project_path / 'slides',
            'notes': project_path / 'notes',
            'templates': project_path / '_templates',
            'resources': project_path / 'resources',
            'output': project_path / 'output'
        }
        
        for dir_path in directories.values():
            dir_path.mkdir(exist_ok=True)
        
        # Create _quarto.yml project file
        quarto_yml = self._create_project_config(project_name)
        project_config_path = project_path / '_quarto.yml'
        project_config_path.write_text(quarto_yml, encoding='utf-8')
        
        # Create .gitignore
        gitignore_content = self._create_gitignore()
        gitignore_path = project_path / '.gitignore'
        gitignore_path.write_text(gitignore_content, encoding='utf-8')
        
        # Create README
        readme_content = self._create_readme(project_name)
        readme_path = project_path / 'README.md'
        readme_path.write_text(readme_content, encoding='utf-8')
        
        file_paths = {
            'project_config': str(project_config_path),
            'gitignore': str(gitignore_path),
            'readme': str(readme_path),
            **{name: str(path) for name, path in directories.items()}
        }
        
        logger.info(f"Created project structure at {project_path}")
        return file_paths
    
    def _create_project_config(self, project_name: str) -> str:
        """Create _quarto.yml project configuration."""
        config = {
            'project': {
                'type': 'default',
                'title': project_name.replace('_', ' ').replace('-', ' ').title()
            },
            'format': {
                'revealjs': {
                    'theme': 'white',
                    'slide-number': True,
                    'chalkboard': True,
                    'preview-links': 'auto',
                    'logo': None,
                    'footer': None
                },
                'pdf': {
                    'documentclass': 'article',
                    'toc': True,
                    'number-sections': True,
                    'colorlinks': True,
                    'geometry': 'margin=1in'
                },
                'html': {
                    'theme': 'cosmo',
                    'toc': True,
                    'number-sections': True
                }
            },
            'execute': {
                'freeze': 'auto'
            }
        }
        
        return yaml.dump(config, default_flow_style=False)
    
    def _create_gitignore(self) -> str:
        """Create .gitignore for Quarto project."""
        return """# Quarto
/.quarto/
/_site/
/output/

# LaTeX
*.aux
*.bbl
*.blg
*.fdb_latexmk
*.fls
*.log
*.out
*.synctex.gz
*.toc
*.nav
*.snm
*.vrb

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# R
.Rproj.user/
.Rhistory
.RData
.Ruserdata

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
"""
    
    def _create_readme(self, project_name: str) -> str:
        """Create README.md for the project."""
        title = project_name.replace('_', ' ').replace('-', ' ').title()
        return f"""# {title}

This is a Quarto project for generating academic slides and lecture notes.

## Structure

- `slides/` - Slide presentations (.qmd files)
- `notes/` - Lecture notes (.qmd files)
- `_templates/` - Custom templates and themes
- `resources/` - Images, data, and other resources
- `output/` - Generated output files

## Usage

### Generate Slides

```bash
quarto render slides/lecture.qmd --to revealjs
```

### Generate Notes

```bash
quarto render notes/lecture.qmd --to pdf
```

### Batch Processing

```bash
quarto render
```

## Customization

- Edit `_quarto.yml` to change project-wide settings
- Add custom themes in `_templates/`
- Modify individual document YAML frontmatter for specific customizations

## Requirements

- Quarto >= 1.4.0
- LaTeX distribution (for PDF output)
- Python (for custom processing scripts)
"""
    
    def generate_yaml_frontmatter(self, config: Dict[str, Any]) -> str:
        """
        Generate YAML frontmatter from configuration dictionary.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            YAML frontmatter string with delimiters
        """
        yaml_content = yaml.dump(config, default_flow_style=False, sort_keys=False)
        return f"---\n{yaml_content}---\n\n"
    
    def load_project_config(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load project configuration from _quarto.yml.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Project configuration dictionary
        """
        if project_path:
            config_file = Path(project_path) / '_quarto.yml'
        else:
            config_file = self.project_dir / '_quarto.yml'
        
        if not config_file.exists():
            logger.warning(f"No _quarto.yml found at {config_file}")
            return {}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.debug(f"Loaded project config from {config_file}")
            return config or {}
        except Exception as e:
            logger.error(f"Error loading project config: {e}")
            return {}
    
    def update_project_config(
        self,
        updates: Dict[str, Any],
        project_path: Optional[str] = None
    ) -> bool:
        """
        Update project configuration file.
        
        Args:
            updates: Configuration updates to apply
            project_path: Path to project directory
            
        Returns:
            True if successful, False otherwise
        """
        if project_path:
            config_file = Path(project_path) / '_quarto.yml'
        else:
            config_file = self.project_dir / '_quarto.yml'
        
        try:
            # Load existing config
            current_config = self.load_project_config(project_path)
            
            # Apply updates (deep merge)
            updated_config = self._deep_merge(current_config, updates)
            
            # Write back to file
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(updated_config, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Updated project config at {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating project config: {e}")
            return False
    
    def _deep_merge(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result