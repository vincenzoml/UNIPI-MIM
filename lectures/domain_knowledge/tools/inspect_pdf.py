#!/usr/bin/env python
"""Inspect PDF: report page count and size.
Usage: python inspect_pdf.py path1.pdf [path2.pdf ...]
"""
from __future__ import annotations
import sys
from pathlib import Path
from PyPDF2 import PdfReader

def inspect(path: Path):
    try:
        reader = PdfReader(str(path))
        pages = len(reader.pages)
    except Exception as e:
        pages = -1
        err = str(e)
    else:
        err = ''
    size = path.stat().st_size if path.exists() else 0
    return path.name, size, pages, err

def main():
    if len(sys.argv) < 2:
        print('Provide at least one PDF path')
        return 1
    print(f"{'FILE':<45} {'BYTES':>10} {'PAGES':>6}  NOTE")
    for arg in sys.argv[1:]:
        p = Path(arg)
        if not p.exists():
            print(f"{p.name:<45} {'-':>10} {'-':>6}  MISSING")
            continue
        name, size, pages, err = inspect(p)
        note = []
        if pages > 120:
            note.append('LARGE_PAGE_COUNT')
        if size > 35_000_000:
            note.append('VERY_LARGE_SIZE')
        if 'book' in name.lower():
            note.append('NAME_HINT_BOOK')
        if err:
            note.append('ERROR:' + err.split('\n')[0][:60])
        print(f"{name:<45} {size:>10} {pages:>6}  {';'.join(note)}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
