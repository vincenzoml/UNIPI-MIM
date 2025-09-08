"""
LaTeX Processor - Advanced LaTeX validation and processing system.

Provides robust LaTeX expression validation, syntax checking, and error reporting
with line numbers for malformed LaTeX expressions. Enhances Quarto's built-in
LaTeX support with comprehensive validation and custom command handling.
"""

import re
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set, Any
from dataclasses import dataclass
from enum import Enum

from ..utils.logger import get_logger
from ..utils.exceptions import handle_exception, InputError

logger = get_logger(__name__)


class LaTeXExpressionType(Enum):
    """Types of LaTeX expressions found in markdown."""
    INLINE_MATH = "inline_math"  # $...$
    DISPLAY_MATH = "display_math"  # $$...$$
    ENVIRONMENT = "environment"  # \begin{...}...\end{...}
    COMMAND = "command"  # \command{...}
    SYMBOL = "symbol"  # \alpha, \beta, etc.


@dataclass
class LaTeXExpression:
    """Represents a LaTeX expression found in markdown content."""
    content: str
    expression_type: LaTeXExpressionType
    line_number: int
    column_start: int
    column_end: int
    is_valid: bool = True
    error_message: Optional[str] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []


@dataclass
class LaTeXValidationResult:
    """Result of LaTeX validation process."""
    is_valid: bool
    expressions: List[LaTeXExpression]
    errors: List[str]
    warnings: List[str]
    packages_required: Set[str]
    custom_commands: Set[str]
    
    def __post_init__(self):
        if not hasattr(self, 'packages_required'):
            self.packages_required = set()
        if not hasattr(self, 'custom_commands'):
            self.custom_commands = set()


class LaTeXExpressionParser:
    """
    Parser for extracting and categorizing LaTeX expressions from markdown.
    
    Handles inline math, display math, environments, commands, and symbols
    with precise line and column tracking for error reporting.
    """
    
    # LaTeX expression patterns
    PATTERNS = {
        LaTeXExpressionType.INLINE_MATH: r'\$([^$\n]+?)\$',
        LaTeXExpressionType.DISPLAY_MATH: r'\$\$([^$]+?)\$\$',
        LaTeXExpressionType.ENVIRONMENT: r'\\begin\{([^}]+)\}(.*?)\\end\{\1\}',
        LaTeXExpressionType.COMMAND: r'\\([a-zA-Z]+)(?:\{([^}]*)\})?',
        LaTeXExpressionType.SYMBOL: r'\\([a-zA-Z]+)(?![a-zA-Z])'
    }
    
    # Common LaTeX packages and their commands
    PACKAGE_COMMANDS = {
        'amsmath': {
            'align', 'equation', 'gather', 'multline', 'split', 'aligned',
            'gathered', 'cases', 'matrix', 'pmatrix', 'bmatrix', 'vmatrix',
            'Vmatrix', 'smallmatrix', 'substack', 'overset', 'underset'
        },
        'amssymb': {
            'mathbb', 'mathfrak', 'mathcal', 'varnothing', 'nexists',
            'complement', 'blacksquare', 'QED', 'bigstar', 'checkmark'
        },
        'amsthm': {
            'theorem', 'lemma', 'corollary', 'proposition', 'definition',
            'example', 'remark', 'proof', 'qed'
        },
        'physics': {
            'derivative', 'partialderivative', 'variation', 'functionalderivative',
            'gradient', 'divergence', 'curl', 'laplacian', 'abs', 'norm',
            'eval', 'order', 'commutator', 'anticommutator', 'poissonbracket'
        },
        'siunitx': {
            'si', 'SI', 'num', 'ang', 'unit', 'qty', 'qtyrange', 'numrange'
        },
        'tikz': {
            'tikzpicture', 'node', 'draw', 'fill', 'path', 'coordinate',
            'tikzset', 'usetikzlibrary'
        }
    }
    
    # Standard LaTeX math symbols (no package required)
    STANDARD_SYMBOLS = {
        'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
        'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'rho', 'sigma',
        'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega', 'Gamma', 'Delta',
        'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Upsilon', 'Phi', 'Psi', 'Omega',
        'sum', 'prod', 'int', 'oint', 'iint', 'iiint', 'lim', 'sup', 'inf',
        'max', 'min', 'arg', 'ker', 'dim', 'hom', 'det', 'exp', 'ln', 'log',
        'sin', 'cos', 'tan', 'sec', 'csc', 'cot', 'sinh', 'cosh', 'tanh',
        'arcsin', 'arccos', 'arctan', 'frac', 'sqrt', 'cdot', 'times', 'div',
        'pm', 'mp', 'leq', 'geq', 'neq', 'approx', 'equiv', 'sim', 'simeq',
        'propto', 'parallel', 'perp', 'subset', 'supset', 'subseteq', 'supseteq',
        'in', 'notin', 'ni', 'cup', 'cap', 'setminus', 'emptyset', 'varnothing',
        'forall', 'exists', 'nexists', 'neg', 'land', 'lor', 'implies', 'iff',
        'leftarrow', 'rightarrow', 'leftrightarrow', 'Leftarrow', 'Rightarrow',
        'Leftrightarrow', 'uparrow', 'downarrow', 'updownarrow', 'nearrow',
        'searrow', 'swarrow', 'nwarrow', 'mapsto', 'longmapsto', 'hookrightarrow',
        'hookleftarrow', 'rightharpoonup', 'rightharpoondown', 'leftharpoonup',
        'leftharpoondown', 'rightleftharpoons', 'infty', 'partial', 'nabla',
        'triangle', 'square', 'diamond', 'star', 'dagger', 'ddagger', 'sharp',
        'flat', 'natural', 'clubsuit', 'diamondsuit', 'heartsuit', 'spadesuit'
    }
    
    def __init__(self):
        self.expressions: List[LaTeXExpression] = []
        self.required_packages: Set[str] = set()
        self.custom_commands: Set[str] = set()
    
    def parse_expressions(self, content: str) -> List[LaTeXExpression]:
        """
        Parse all LaTeX expressions from markdown content.
        
        Args:
            content: Markdown content to parse
            
        Returns:
            List of LaTeXExpression objects with location information
        """
        self.expressions = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Parse different types of expressions
            self._parse_display_math(line, line_num)
            self._parse_inline_math(line, line_num)
            self._parse_environments(line, line_num, lines, line_num - 1)
            self._parse_commands_and_symbols(line, line_num)
        
        return self.expressions
    
    def _parse_inline_math(self, line: str, line_num: int):
        """Parse inline math expressions ($...$)."""
        pattern = self.PATTERNS[LaTeXExpressionType.INLINE_MATH]
        
        for match in re.finditer(pattern, line):
            expression = LaTeXExpression(
                content=match.group(1),
                expression_type=LaTeXExpressionType.INLINE_MATH,
                line_number=line_num,
                column_start=match.start(),
                column_end=match.end()
            )
            self.expressions.append(expression)
    
    def _parse_display_math(self, line: str, line_num: int):
        """Parse display math expressions ($$...$$)."""
        pattern = self.PATTERNS[LaTeXExpressionType.DISPLAY_MATH]
        
        for match in re.finditer(pattern, line):
            expression = LaTeXExpression(
                content=match.group(1),
                expression_type=LaTeXExpressionType.DISPLAY_MATH,
                line_number=line_num,
                column_start=match.start(),
                column_end=match.end()
            )
            self.expressions.append(expression)
    
    def _parse_environments(self, line: str, line_num: int, all_lines: List[str], line_index: int):
        """Parse LaTeX environments (\begin{...}...\end{...})."""
        begin_pattern = r'\\begin\{([^}]+)\}'
        
        for match in re.finditer(begin_pattern, line):
            env_name = match.group(1)
            env_content = self._extract_environment_content(
                all_lines, line_index, env_name, match.start()
            )
            
            if env_content:
                expression = LaTeXExpression(
                    content=env_content['content'],
                    expression_type=LaTeXExpressionType.ENVIRONMENT,
                    line_number=line_num,
                    column_start=match.start(),
                    column_end=env_content['end_column']
                )
                self.expressions.append(expression)
    
    def _extract_environment_content(
        self, 
        lines: List[str], 
        start_line_index: int, 
        env_name: str, 
        start_col: int
    ) -> Optional[Dict[str, Any]]:
        """Extract content of a LaTeX environment across multiple lines."""
        content_lines = []
        end_pattern = f'\\\\end\\{{{env_name}\\}}'
        
        # Start from the current line
        current_line = lines[start_line_index]
        begin_pos = current_line.find(f'\\begin{{{env_name}}}', start_col)
        
        if begin_pos == -1:
            return None
        
        # Add content after \begin{env} on the same line
        after_begin = current_line[begin_pos + len(f'\\begin{{{env_name}}}'):]
        content_lines.append(after_begin)
        
        # Look for \end{env} in subsequent lines
        for line_index in range(start_line_index + 1, len(lines)):
            line = lines[line_index]
            end_match = re.search(end_pattern, line)
            
            if end_match:
                # Found end, add content before \end{env}
                before_end = line[:end_match.start()]
                content_lines.append(before_end)
                
                return {
                    'content': '\n'.join(content_lines).strip(),
                    'end_line': line_index + 1,
                    'end_column': end_match.end()
                }
            else:
                # Add entire line to content
                content_lines.append(line)
        
        # Environment not closed
        return None
    
    def _parse_commands_and_symbols(self, line: str, line_num: int):
        """Parse LaTeX commands and symbols."""
        # Parse commands with arguments
        command_pattern = self.PATTERNS[LaTeXExpressionType.COMMAND]
        
        for match in re.finditer(command_pattern, line):
            command_name = match.group(1)
            command_args = match.group(2) if match.group(2) else ""
            
            expression = LaTeXExpression(
                content=f"\\{command_name}" + (f"{{{command_args}}}" if command_args else ""),
                expression_type=LaTeXExpressionType.COMMAND,
                line_number=line_num,
                column_start=match.start(),
                column_end=match.end()
            )
            self.expressions.append(expression)
            
            # Track required packages
            self._track_package_requirements(command_name)
        
        # Parse standalone symbols
        symbol_pattern = self.PATTERNS[LaTeXExpressionType.SYMBOL]
        
        for match in re.finditer(symbol_pattern, line):
            symbol_name = match.group(1)
            
            # Skip if already captured as command
            if any(expr.line_number == line_num and 
                   expr.column_start <= match.start() < expr.column_end 
                   for expr in self.expressions):
                continue
            
            expression = LaTeXExpression(
                content=f"\\{symbol_name}",
                expression_type=LaTeXExpressionType.SYMBOL,
                line_number=line_num,
                column_start=match.start(),
                column_end=match.end()
            )
            self.expressions.append(expression)
            
            # Track required packages
            self._track_package_requirements(symbol_name)
    
    def _track_package_requirements(self, command_or_symbol: str):
        """Track which LaTeX packages are required for commands/symbols."""
        for package, commands in self.PACKAGE_COMMANDS.items():
            if command_or_symbol in commands:
                self.required_packages.add(package)
                return
        
        # Check if it's a standard symbol
        if command_or_symbol not in self.STANDARD_SYMBOLS:
            # Might be a custom command
            self.custom_commands.add(command_or_symbol)


class LaTeXValidator:
    """
    Validates LaTeX expressions for syntax correctness and completeness.
    
    Provides detailed error messages with line numbers and suggestions
    for fixing common LaTeX syntax errors.
    """
    
    # Common LaTeX syntax errors and their patterns
    SYNTAX_ERROR_PATTERNS = {
        r'\\begin\{([^}]+)\}(?!.*\\end\{\1\})': "Unclosed environment: \\begin{{{0}}} without matching \\end{{{0}}}",
        r'\\end\{([^}]+)\}': "Unmatched \\end{{{0}}} without corresponding \\begin{{{0}}}",
        r'\{[^}]*$': "Unclosed brace: missing closing '}'",
        r'^[^{]*\}': "Unmatched closing brace: extra '}'",
        r'\\[a-zA-Z]+\{[^}]*\{[^}]*\}[^}]*$': "Nested braces may be unbalanced",
        r'\$[^$]*\n[^$]*\$': "Inline math spans multiple lines (use $$ for display math)",
        r'\\\\(?![a-zA-Z])': "Double backslash \\\\ should be used only for line breaks in math environments"
    }
    
    # Common mistakes and suggestions
    COMMON_MISTAKES = {
        r'\\frac\{([^}]+)\}\{([^}]+)\}': {
            'check': lambda m: '/' in m.group(1) or '/' in m.group(2),
            'suggestion': "Use \\frac{numerator}{denominator} instead of fractions with /"
        },
        r'\\sqrt\[([^\]]+)\]\{([^}]+)\}': {
            'check': lambda m: True,
            'suggestion': "For nth roots, use \\sqrt[n]{x} syntax"
        },
        r'([a-zA-Z])\s*\*\s*([a-zA-Z])': {
            'check': lambda m: True,
            'suggestion': "Use \\cdot or \\times for multiplication instead of *"
        },
        r'([a-zA-Z])\s*/\s*([a-zA-Z])': {
            'check': lambda m: True,
            'suggestion': "Use \\frac{a}{b} for fractions instead of a/b"
        }
    }
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_expressions(self, expressions: List[LaTeXExpression]) -> LaTeXValidationResult:
        """
        Validate a list of LaTeX expressions.
        
        Args:
            expressions: List of LaTeX expressions to validate
            
        Returns:
            LaTeXValidationResult with validation details
        """
        self.errors = []
        self.warnings = []
        all_packages = set()
        all_custom_commands = set()
        
        for expr in expressions:
            self._validate_single_expression(expr)
            
            # Collect package requirements
            parser = LaTeXExpressionParser()
            parser._track_package_requirements(self._extract_command_name(expr.content))
            all_packages.update(parser.required_packages)
            all_custom_commands.update(parser.custom_commands)
        
        # Validate environment matching across expressions
        self._validate_environment_matching(expressions)
        
        # Check for common syntax issues
        self._check_common_syntax_issues(expressions)
        
        is_valid = len(self.errors) == 0
        
        return LaTeXValidationResult(
            is_valid=is_valid,
            expressions=expressions,
            errors=self.errors,
            warnings=self.warnings,
            packages_required=all_packages,
            custom_commands=all_custom_commands
        )
    
    def _validate_single_expression(self, expr: LaTeXExpression):
        """Validate a single LaTeX expression."""
        content = expr.content
        
        # Check for basic syntax issues
        if not self._check_brace_balance(content):
            expr.is_valid = False
            expr.error_message = f"Unbalanced braces in LaTeX expression"
            expr.suggestions.append("Check that every {{ has a matching }}")
            self.errors.append(f"Line {expr.line_number}: Unbalanced braces in '{content}'")
        
        # Check for empty expressions
        if not content.strip():
            expr.is_valid = False
            expr.error_message = "Empty LaTeX expression"
            self.errors.append(f"Line {expr.line_number}: Empty LaTeX expression")
        
        # Check for invalid characters
        if self._has_invalid_characters(content):
            expr.is_valid = False
            expr.error_message = "Invalid characters in LaTeX expression"
            expr.suggestions.append("LaTeX expressions should contain only valid LaTeX commands and math symbols")
            self.errors.append(f"Line {expr.line_number}: Invalid characters in '{content}'")
        
        # Check for common mistakes
        self._check_common_mistakes(expr)
    
    def _check_brace_balance(self, content: str) -> bool:
        """Check if braces are balanced in LaTeX content."""
        brace_count = 0
        i = 0
        
        while i < len(content):
            if content[i] == '\\' and i + 1 < len(content):
                # Skip escaped characters
                i += 2
                continue
            elif content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count < 0:
                    return False
            i += 1
        
        return brace_count == 0
    
    def _has_invalid_characters(self, content: str) -> bool:
        """Check for invalid characters in LaTeX content."""
        # Allow letters, numbers, spaces, common math symbols, and LaTeX commands
        valid_pattern = r'^[a-zA-Z0-9\s\\{}()[\].,;:!?+\-*/=<>^_|~`\'\"&%$#@]*$'
        return not re.match(valid_pattern, content)
    
    def _check_common_mistakes(self, expr: LaTeXExpression):
        """Check for common LaTeX mistakes and provide suggestions."""
        content = expr.content
        
        for pattern, mistake_info in self.COMMON_MISTAKES.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                if mistake_info['check'](match):
                    expr.suggestions.append(mistake_info['suggestion'])
                    self.warnings.append(
                        f"Line {expr.line_number}: {mistake_info['suggestion']} in '{content}'"
                    )
    
    def _validate_environment_matching(self, expressions: List[LaTeXExpression]):
        """Validate that LaTeX environments are properly matched."""
        env_stack = []
        
        for expr in expressions:
            if expr.expression_type == LaTeXExpressionType.ENVIRONMENT:
                content = expr.content
                
                # Find \begin{env} and \end{env} pairs
                begin_matches = re.finditer(r'\\begin\{([^}]+)\}', content)
                end_matches = re.finditer(r'\\end\{([^}]+)\}', content)
                
                begins = [(m.group(1), m.start()) for m in begin_matches]
                ends = [(m.group(1), m.start()) for m in end_matches]
                
                # Check if environments are properly nested
                for env_name, pos in begins:
                    env_stack.append((env_name, expr.line_number, pos))
                
                for env_name, pos in ends:
                    if not env_stack:
                        self.errors.append(
                            f"Line {expr.line_number}: Unmatched \\end{{{env_name}}}"
                        )
                        continue
                    
                    last_env, last_line, last_pos = env_stack.pop()
                    if last_env != env_name:
                        self.errors.append(
                            f"Line {expr.line_number}: Environment mismatch - "
                            f"\\begin{{{last_env}}} at line {last_line} closed with \\end{{{env_name}}}"
                        )
        
        # Check for unclosed environments
        for env_name, line_num, pos in env_stack:
            self.errors.append(f"Line {line_num}: Unclosed environment \\begin{{{env_name}}}")
    
    def _check_common_syntax_issues(self, expressions: List[LaTeXExpression]):
        """Check for common LaTeX syntax issues across all expressions."""
        for expr in expressions:
            content = expr.content
            
            # Check for specific syntax patterns
            for pattern, error_template in self.SYNTAX_ERROR_PATTERNS.items():
                matches = re.finditer(pattern, content)
                for match in matches:
                    if match.groups():
                        error_msg = error_template.format(*match.groups())
                    else:
                        error_msg = error_template
                    
                    self.errors.append(f"Line {expr.line_number}: {error_msg}")
    
    def _extract_command_name(self, content: str) -> str:
        """Extract the main command name from LaTeX content."""
        match = re.search(r'\\([a-zA-Z]+)', content)
        return match.group(1) if match else ""


class LaTeXProcessor:
    """
    Main LaTeX processing system with validation, error reporting, and package management.
    
    Provides comprehensive LaTeX processing capabilities including expression validation,
    syntax checking, package requirement detection, and detailed error reporting with
    line numbers and suggestions for fixes.
    """
    
    def __init__(self):
        self.parser = LaTeXExpressionParser()
        self.validator = LaTeXValidator()
        self.last_validation_result: Optional[LaTeXValidationResult] = None
    
    @handle_exception
    def process_content(self, content: str) -> LaTeXValidationResult:
        """
        Process markdown content for LaTeX expressions with full validation.
        
        Args:
            content: Markdown content containing LaTeX expressions
            
        Returns:
            LaTeXValidationResult with validation details and requirements
            
        Raises:
            InputError: If content processing fails
        """
        logger.info("Processing LaTeX expressions in markdown content")
        
        try:
            # Parse all LaTeX expressions
            expressions = self.parser.parse_expressions(content)
            logger.debug(f"Found {len(expressions)} LaTeX expressions")
            
            # Validate expressions
            validation_result = self.validator.validate_expressions(expressions)
            self.last_validation_result = validation_result
            
            # Log results
            if validation_result.is_valid:
                logger.info(f"All {len(expressions)} LaTeX expressions are valid")
            else:
                logger.warning(f"Found {len(validation_result.errors)} LaTeX errors")
                for error in validation_result.errors:
                    logger.error(f"LaTeX Error: {error}")
            
            if validation_result.warnings:
                logger.info(f"Found {len(validation_result.warnings)} LaTeX warnings")
                for warning in validation_result.warnings:
                    logger.warning(f"LaTeX Warning: {warning}")
            
            # Log package requirements
            if validation_result.packages_required:
                logger.info(f"Required LaTeX packages: {', '.join(sorted(validation_result.packages_required))}")
            
            if validation_result.custom_commands:
                logger.info(f"Custom commands detected: {', '.join(sorted(validation_result.custom_commands))}")
            
            return validation_result
            
        except Exception as e:
            raise InputError(f"Error processing LaTeX content: {e}")
    
    def validate_latex_syntax(self, latex_code: str, line_number: int = 1) -> Tuple[bool, List[str]]:
        """
        Validate LaTeX syntax using external LaTeX compiler.
        
        Args:
            latex_code: LaTeX code to validate
            line_number: Line number for error reporting
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        logger.debug(f"Validating LaTeX syntax at line {line_number}")
        
        # Create minimal LaTeX document for testing
        test_document = f"""
\\documentclass{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{amsthm}}
\\begin{{document}}
{latex_code}
\\end{{document}}
"""
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
                f.write(test_document)
                tex_file = f.name
            
            # Try to compile with LaTeX
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', 
                 str(Path(tex_file).parent), tex_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up temporary files
            tex_path = Path(tex_file)
            for ext in ['.tex', '.pdf', '.log', '.aux']:
                temp_file = tex_path.with_suffix(ext)
                if temp_file.exists():
                    temp_file.unlink()
            
            if result.returncode == 0:
                return True, []
            else:
                # Parse LaTeX errors
                errors = self._parse_latex_errors(result.stdout + result.stderr, line_number)
                return False, errors
                
        except subprocess.TimeoutExpired:
            return False, [f"Line {line_number}: LaTeX compilation timed out"]
        except FileNotFoundError:
            logger.warning("LaTeX compiler not found, skipping syntax validation")
            return True, []  # Assume valid if no compiler available
        except Exception as e:
            return False, [f"Line {line_number}: Error validating LaTeX: {e}"]
    
    def _parse_latex_errors(self, latex_output: str, base_line: int) -> List[str]:
        """Parse LaTeX compiler output for error messages."""
        errors = []
        lines = latex_output.split('\n')
        
        for line in lines:
            # Look for LaTeX error patterns
            if line.startswith('!') or 'Error:' in line or 'error:' in line:
                # Clean up the error message
                clean_error = re.sub(r'^!\s*', '', line).strip()
                if clean_error:
                    errors.append(f"Line {base_line}: {clean_error}")
        
        return errors
    
    def get_required_packages(self) -> Set[str]:
        """Get the set of LaTeX packages required for the last processed content."""
        if self.last_validation_result:
            return self.last_validation_result.packages_required
        return set()
    
    def get_custom_commands(self) -> Set[str]:
        """Get the set of custom LaTeX commands detected in the last processed content."""
        if self.last_validation_result:
            return self.last_validation_result.custom_commands
        return set()
    
    def generate_package_header(self, additional_packages: Optional[List[str]] = None) -> str:
        """
        Generate LaTeX package header based on detected requirements.
        
        Args:
            additional_packages: Optional additional packages to include
            
        Returns:
            LaTeX package header string
        """
        packages = self.get_required_packages().copy()
        
        if additional_packages:
            packages.update(additional_packages)
        
        # Always include basic math packages
        packages.update(['amsmath', 'amssymb', 'amsthm'])
        
        header_lines = []
        for package in sorted(packages):
            header_lines.append(f"\\usepackage{{{package}}}")
        
        return '\n'.join(header_lines)
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of the last validation results."""
        if not self.last_validation_result:
            return {"status": "No validation performed"}
        
        result = self.last_validation_result
        
        return {
            "status": "valid" if result.is_valid else "invalid",
            "total_expressions": len(result.expressions),
            "errors": len(result.errors),
            "warnings": len(result.warnings),
            "packages_required": list(result.packages_required),
            "custom_commands": list(result.custom_commands),
            "expression_types": {
                expr_type.value: sum(1 for expr in result.expressions 
                                   if expr.expression_type == expr_type)
                for expr_type in LaTeXExpressionType
            }
        }