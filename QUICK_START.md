# Quick Start with run.py

The `run.py` script is a one-stop solution for setting up and running the UNIPI-MIM lecture slides server.

## Features

- 🔧 **Auto-setup**: Creates virtual environment and installs all dependencies
- 🚀 **Live Server**: Serves slides with hot reloading
- 🌐 **Browser Integration**: Automatically opens slides and notes
- 📱 **Mobile Friendly**: Responsive RevealJS slides
- 📚 **Dual Output**: Both presentation slides and detailed notes
- 🔄 **Watch Mode**: Automatically rebuilds when files change

## Quick Start

```bash
git clone <repo-url>
cd UNIPI-MIM
python run.py
```

That's it! The script will:
1. Set up a Python virtual environment in `.venv/`
2. Install all required dependencies
3. Install the markdown-slides-generator app
4. Start serving `lectures/Lecture 01/Lecture_notes.md`
5. Open your browser to http://localhost:8000

## Usage Options

```bash
# Basic usage - setup and serve
python run.py

# Use specific Python version
python run.py --python 3.11

# Force recreate virtual environment
python run.py --force-recreate

# Just setup, don't start server
python run.py --no-serve

# Serve notes instead of slides
python run.py --notes-only

# View help
python run.py --help
```

## What it serves

Currently hardcoded to serve:
- **Path**: `lectures/Lecture 01/`
- **File**: `Lecture_notes.md`
- **Config**: `config.yaml`
- **Output**: Generated slides and notes with custom theme

## Browser URLs

When the server starts, you can access:
- **Slides**: http://localhost:8000/Lecture_notes_slides.html
- **Notes**: http://localhost:8000/Lecture_notes_notes.html

The script automatically opens the slides view, but you can type `n` to open notes.

## Live Development

- Edit `Lecture_notes.md` and see changes instantly
- Modify styles in `lectures/Lecture 01/styles/`
- Update bibliography in `full_course_references.bib`
- All changes trigger automatic rebuilds

## Stopping the Server

Press `Ctrl+C` to stop the server gracefully.

## Manual Usage

If you prefer manual control:

```bash
# Activate the environment created by run.py
source .venv/bin/activate

# Use the CLI directly
cd "lectures/Lecture 01"
markdown-slides generate -w -s -c config.yaml Lecture_notes.md
```