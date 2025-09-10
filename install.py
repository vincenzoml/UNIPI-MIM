#!/usr/bin/env python3
"""Repository bootstrap installer.
Creates or reuses a Python virtual environment in .venv and installs
combined requirements plus the app in editable mode.

Steps:
1. Create .venv (if absent)
2. Upgrade pip/setuptools/wheel
3. Install requirements from app/requirements.txt
4. Install requirements from lectures/domain_knowledge/requirements.txt (if exists)
5. pip install -e app

Usage:
  python install.py            # standard install
  python install.py --python 3.11  # choose python version if available
  python install.py --force-recreate  # delete and recreate env
"""
from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / '.venv'
APP_REQ = ROOT / 'app' / 'requirements.txt'
DK_REQ = ROOT / 'lectures' / 'domain_knowledge' / 'requirements.txt'


def run(cmd: list[str], **kwargs):
    print(f"[CMD] {' '.join(cmd)}")
    subprocess.check_call(cmd, **kwargs)


def ensure_python(python_spec: str | None) -> str:
    if python_spec:
        # Try `python<spec>` then `python` fallback
        candidates = [f"python{python_spec}", sys.executable]
    else:
        candidates = [sys.executable]
    for c in candidates:
        try:
            subprocess.check_call([c, '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return c
        except Exception:
            continue
    print("ERROR: No suitable Python interpreter found.")
    sys.exit(1)


def create_venv(python: str):
    if not VENV_DIR.exists():
        print(f"[INFO] Creating virtualenv at {VENV_DIR}")
        run([python, '-m', 'venv', str(VENV_DIR)])
    else:
        print(f"[INFO] Reusing existing virtualenv at {VENV_DIR}")


def pip_path() -> str:
    if sys.platform == 'win32':
        return str(VENV_DIR / 'Scripts' / 'pip')
    return str(VENV_DIR / 'bin' / 'pip')


def install_requirements():
    pip = pip_path()
    run([pip, 'install', '--upgrade', 'pip', 'setuptools', 'wheel'])
    if APP_REQ.exists():
        run([pip, 'install', '-r', str(APP_REQ)])
    else:
        print('[WARN] app requirements not found.')
    if DK_REQ.exists():
        run([pip, 'install', '-r', str(DK_REQ)])
    else:
        print('[INFO] domain knowledge requirements not found (optional).')
    # Editable install of app
    app_dir = ROOT / 'app'
    if app_dir.exists():
        run([pip, 'install', '-e', str(app_dir)])
    else:
        print('[WARN] app directory not found; skipping editable install.')


def parse_args():
    p = argparse.ArgumentParser(description='Bootstrap repository environment')
    p.add_argument('--python', help='Python version spec (e.g., 3.11)')
    p.add_argument('--force-recreate', action='store_true', help='Delete and recreate existing .venv')
    return p.parse_args()


def main():
    args = parse_args()
    if args.force_recreate and VENV_DIR.exists():
        print('[INFO] Removing existing virtualenv')
        shutil.rmtree(VENV_DIR)
    python_exec = ensure_python(args.python)
    create_venv(python_exec)
    install_requirements()
    print('\n[SUCCESS] Environment setup complete. Activate with:')
    if sys.platform == 'win32':
        print('  .venv\\Scripts\\activate')
    else:
        print('  source .venv/bin/activate')

if __name__ == '__main__':
    main()
