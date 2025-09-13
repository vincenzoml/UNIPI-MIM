#!/usr/bin/env python3
"""Repository runner script.

This script ensures the virtual environment is properly set up and then
uses the markdown-slides-generator app to serve the lecture notes with 
live reloading and web server functionality.

Features:
1. Creates or reuses a Python virtual environment in .venv
2. Installs all required dependencies (app + domain knowledge requirements)
3. Installs the app in editable mode  
4. Serves the lecture notes with live reloading from hardcoded lecture path
5. Opens browser automatically to view slides and notes

Usage:
  python run.py                    # standard run with auto-setup
  python run.py --python 3.11     # choose python version if available
  python run.py --force-recreate  # delete and recreate env first
  python run.py --no-serve        # just setup, don't serve
  python run.py --notes-only      # serve notes instead of slides

The script will serve lectures/Lecture 01/Lecture_notes.md by default.

Example workflow:
  1. git clone <repo>
  2. cd <repo>
  3. python run.py               # One command setup and serve!
  4. Open http://localhost:8000 in browser
  5. Edit Lecture_notes.md and see live updates
  6. Press Ctrl+C to stop
"""
from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / '.venv'
APP_REQ = ROOT / 'app' / 'requirements.txt'
DK_REQ = ROOT / 'lectures' / 'domain_knowledge' / 'requirements.txt'

# Hardcoded lecture path
LECTURE_PATH = ROOT / 'lectures' / 'Lecture 01'
LECTURE_FILE = LECTURE_PATH / 'Lecture_notes.md'
CONFIG_FILE = LECTURE_PATH / 'config.yaml'


def run(cmd: list[str], **kwargs):
    """Execute a shell command with logging."""
    print(f"[CMD] {' '.join(cmd)}")
    subprocess.check_call(cmd, **kwargs)


def run_capture(cmd: list[str], **kwargs) -> str:
    """Execute a shell command and return output."""
    print(f"[CMD] {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        print(f"[ERROR] Command failed: {' '.join(cmd)}")
        print(f"[ERROR] stderr: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result.stdout.strip()


def ensure_python(python_spec: str | None) -> str:
    """Find and validate a suitable Python interpreter."""
    if python_spec:
        # Try `python<spec>` then `python` fallback
        candidates = [f"python{python_spec}", sys.executable]
    else:
        candidates = [sys.executable]
    
    for c in candidates:
        try:
            subprocess.check_call([c, '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            version = run_capture([c, '--version'])
            print(f"[INFO] Using Python: {c} ({version})")
            return c
        except Exception:
            continue
    
    print("ERROR: No suitable Python interpreter found.")
    sys.exit(1)


def create_venv(python: str, force_recreate: bool = False):
    """Create or reuse virtual environment."""
    if force_recreate and VENV_DIR.exists():
        print(f'[INFO] Removing existing virtualenv at {VENV_DIR}')
        shutil.rmtree(VENV_DIR)
    
    if not VENV_DIR.exists():
        print(f"[INFO] Creating virtualenv at {VENV_DIR}")
        run([python, '-m', 'venv', str(VENV_DIR)])
    else:
        print(f"[INFO] Reusing existing virtualenv at {VENV_DIR}")


def get_venv_paths():
    """Get paths for venv executables."""
    if sys.platform == 'win32':
        pip_path = VENV_DIR / 'Scripts' / 'pip'
        python_path = VENV_DIR / 'Scripts' / 'python.exe'
        activate_path = VENV_DIR / 'Scripts' / 'activate'
    else:
        pip_path = VENV_DIR / 'bin' / 'pip'
        python_path = VENV_DIR / 'bin' / 'python'
        activate_path = VENV_DIR / 'bin' / 'activate'
    
    return str(pip_path), str(python_path), str(activate_path)


def install_requirements():
    """Install all requirements and the app in editable mode."""
    pip, python, activate = get_venv_paths()
    
    print("[INFO] Upgrading pip, setuptools, wheel...")
    run([pip, 'install', '--upgrade', 'pip', 'setuptools', 'wheel'])
    
    if APP_REQ.exists():
        print(f"[INFO] Installing app requirements from {APP_REQ}")
        run([pip, 'install', '-r', str(APP_REQ)])
    else:
        print('[WARN] app requirements not found.')
    
    if DK_REQ.exists():
        print(f"[INFO] Installing domain knowledge requirements from {DK_REQ}")
        run([pip, 'install', '-r', str(DK_REQ)])
    else:
        print('[INFO] domain knowledge requirements not found (optional).')
    
    # Editable install of app
    app_dir = ROOT / 'app'
    if app_dir.exists():
        print(f"[INFO] Installing app in editable mode from {app_dir}")
        run([pip, 'install', '-e', str(app_dir)])
    else:
        print('[ERROR] app directory not found; cannot install app.')
        sys.exit(1)


def verify_lecture_setup():
    """Verify that the lecture files exist."""
    if not LECTURE_PATH.exists():
        print(f'[ERROR] Lecture path does not exist: {LECTURE_PATH}')
        sys.exit(1)
    
    if not LECTURE_FILE.exists():
        print(f'[ERROR] Lecture file does not exist: {LECTURE_FILE}')
        sys.exit(1)
    
    if not CONFIG_FILE.exists():
        print(f'[WARN] Config file not found: {CONFIG_FILE}')
        print('[INFO] Will use default configuration')
    
    print(f'[INFO] Lecture setup verified:')
    print(f'  Path: {LECTURE_PATH}')
    print(f'  File: {LECTURE_FILE}')
    print(f'  Config: {CONFIG_FILE if CONFIG_FILE.exists() else "default"}')


def serve_lecture(notes_only: bool = False):
    """Serve the lecture using markdown-slides-generator."""
    pip, python, activate = get_venv_paths()
    
    print(f'\n[INFO] Starting lecture server...')
    print(f'[INFO] Serving: {LECTURE_FILE}')
    print(f'[INFO] Working directory: {LECTURE_PATH}')
    
    # Build command
    cmd = [python, '-m', 'markdown_slides_generator.cli', 'generate']
    
    # Add watch and serve flags
    cmd.extend(['-w', '-s'])
    
    # Add config if it exists
    if CONFIG_FILE.exists():
        cmd.extend(['-c', str(CONFIG_FILE)])
    
    # Add notes flag if requested
    if notes_only:
        cmd.extend(['--notes-only'])
    
    # Add the markdown file
    cmd.append(str(LECTURE_FILE))
    
    print(f'[INFO] Command: {" ".join(cmd)}')
    print(f'[INFO] Server will start with live reloading enabled')
    print(f'[INFO] Press Ctrl+C to stop the server\n')
    
    # Change to lecture directory and run
    try:
        subprocess.run(cmd, cwd=LECTURE_PATH, check=True)
    except KeyboardInterrupt:
        print('\n[INFO] Server stopped by user')
    except subprocess.CalledProcessError as e:
        print(f'\n[ERROR] Server failed with exit code {e.returncode}')
        sys.exit(e.returncode)


def parse_args():
    """Parse command line arguments."""
    p = argparse.ArgumentParser(description='Setup environment and serve lecture notes')
    p.add_argument('--python', help='Python version spec (e.g., 3.11)')
    p.add_argument('--force-recreate', action='store_true', 
                   help='Delete and recreate existing .venv')
    p.add_argument('--no-serve', action='store_true',
                   help='Just setup environment, do not serve')
    p.add_argument('--notes-only', action='store_true',
                   help='Serve notes instead of slides')
    return p.parse_args()


def print_activation_instructions():
    """Print instructions for manually activating the venv."""
    print('\n[INFO] To manually activate the environment in the future:')
    if sys.platform == 'win32':
        print('  .venv\\Scripts\\activate')
    else:
        print('  source .venv/bin/activate')
    print('  Then use: markdown-slides generate -w -s ...')


def main():
    """Main entry point."""
    args = parse_args()
    
    print('=' * 60)
    print('UNIPI-MIM Lecture Server Runner')
    print('=' * 60)
    
    # 1. Setup environment
    print('\n[STEP 1/4] Setting up Python environment...')
    python_exec = ensure_python(args.python)
    create_venv(python_exec, args.force_recreate)
    
    print('\n[STEP 2/4] Installing requirements...')
    install_requirements()
    
    print('\n[STEP 3/4] Verifying lecture setup...')
    verify_lecture_setup()
    
    if args.no_serve:
        print('\n[STEP 4/4] Skipping server (--no-serve flag)')
        print_activation_instructions()
        print('\n[SUCCESS] Environment setup complete!')
        return
    
    print('\n[STEP 4/4] Starting lecture server...')
    serve_lecture(args.notes_only)
    
    print('\n[SUCCESS] Session complete!')


if __name__ == '__main__':
    main()