# Markdown Slides Generator

Convert academic markdown lecture files into beautiful slides and comprehensive notes using modern tools like Quarto and reveal.js.

## Features

- 🎯 **Single Source of Truth**: Write once in markdown, generate both slides and notes
- 🎨 **Beautiful Slides**: Professional reveal.js themes optimized for academic content
- 📚 **Academic Notes**: Comprehensive PDF notes with proper formatting and TOC
- 🧮 **LaTeX Math**: Full support for mathematical expressions and equations
- 🎛️ **Fine Control**: Special markdown syntax for slide boundaries and content flow
- 📦 **Multiple Formats**: HTML, PDF, PowerPoint, and LaTeX Beamer output
- 🚀 **Batch Processing**: Process entire lecture directories efficiently
- 👁️ **Watch Mode**: Automatic regeneration when files change during development

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/example/markdown-slides-generator.git
cd markdown-slides-generator/app

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Install Quarto (required external dependency)
# macOS:
brew install quarto

# Linux:
# Download from https://quarto.org/docs/get-started/

# Verify installation
markdown-slides check
```

### Basic Usage

```bash
# Generate slides and notes from a markdown file
markdown-slides generate lecture01.md

# Generate only slides in HTML format
markdown-slides generate lecture01.md --slides-only

# Generate multiple formats
markdown-slides generate lecture01.md -f html -f pdf -f pptx

# Process entire lecture directory
markdown-slides batch lectures/ --output-dir presentations/

# Use custom theme and configuration
markdown-slides generate lecture01.md --theme academic --config config.yaml

# Watch mode - automatically regenerate on file changes
markdown-slides generate lecture01.md --watch

# Watch mode with live server and auto-reload in browser
markdown-slides generate lecture01.md --watch --serve
```

## Watch Mode

The watch mode (`-w` or `--watch`) monitors your markdown file for changes and automatically regenerates the output files. This is perfect for development workflows where you want to see changes immediately.

### Basic Watch Mode Features
- Monitors the input file for modifications
- Automatic regeneration on save
- Debounced to prevent excessive regeneration
- Cross-platform file system monitoring
- Graceful keyboard interrupt handling (Ctrl+C)

### Live Server Mode (`--serve`)

When combined with `--serve`, watch mode starts a local HTTP server with **real-time browser auto-reload**:

- 🔥 **Hot Reload**: Browser automatically refreshes when files change
- 🌐 **Local Server**: Serves files at `http://localhost:8000` (customizable port)
- 🚀 **Auto-Open**: Automatically opens your default browser
- 📡 **WebSocket**: Real-time communication for instant updates
- 📱 **Network Access**: Available on local network for mobile testing

### Usage
```bash
# Basic watch mode
markdown-slides generate lecture.md --watch

# Watch mode with live server (recommended for development)
markdown-slides generate lecture.md --watch --serve

# Custom port and disable auto-open
markdown-slides generate lecture.md --watch --serve --port 3000 --no-open

# Watch mode with specific output formats
markdown-slides generate lecture.md --watch --serve -f html

# Watch mode with custom theme
markdown-slides generate lecture.md --watch --serve --theme academic-modern
```

### Tips
- **Live server mode** is perfect for presentation development
- Use watch mode during content creation for immediate feedback
- The initial generation must succeed before watch mode activates
- Files are automatically overwritten in watch mode
- Press Ctrl+C to stop watching and exit
- Live server automatically finds free ports if default is busy

### Limitations
- `--serve` requires `--watch` mode
- `--serve` is not compatible with `--notes-only` (notes are PDFs)
- `--watch` is incompatible with `--dry-run`

## Special Markdown Syntax

Control slide generation with special HTML comments:

```markdown
# Lecture Title

This content appears in both slides and notes.

<!-- SLIDE -->
## New Slide

This starts a new slide.

<!-- SLIDE-ONLY -->
This content only appears in slides.

<!-- NOTES-ONLY -->
This detailed explanation only appears in notes.

<!-- NOTES -->
This starts a new slide AND the content only appears in notes.
Like using --- separator but for notes-only content.

<!-- ALL -->
Back to normal - appears in both slides and notes.

## Math Support

Inline math: $E = mc^2$

Display math:
$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$
```

## Project Structure

```
app/
├── src/markdown_slides_generator/    # Main package
│   ├── __init__.py                   # Package initialization
│   ├── cli.py                        # Command line interface
│   ├── core/                         # Core processing modules
│   │   ├── content_splitter.py       # Markdown directive processing
│   │   └── quarto_orchestrator.py    # Quarto integration
│   └── utils/                        # Utility modules
│       ├── logger.py                 # Logging system
│       └── exceptions.py             # Error handling
├── requirements.txt                  # Dependencies
├── setup.py                         # Package configuration
└── README.md                        # This file
```

## Development

### Setting up Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
isort src/

# Type checking
mypy src/

# Linting
flake8 src/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=markdown_slides_generator

# Run specific test file
pytest tests/test_cli.py
```

## Dependencies

### Required
- **Python 3.8+**: Core runtime
- **Quarto**: Document processing engine (install separately)
- **click**: CLI framework
- **pyyaml**: Configuration file support
- **watchdog**: File system monitoring for watch mode

### Optional
- **LaTeX**: For PDF generation (TeX Live or MiKTeX)
- **rich**: Enhanced terminal output
- **colorama**: Cross-platform colors

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Support

- 📖 [Documentation](https://markdown-slides-generator.readthedocs.io/)
- 🐛 [Issue Tracker](https://github.com/example/markdown-slides-generator/issues)
- 💬 [Discussions](https://github.com/example/markdown-slides-generator/discussions)