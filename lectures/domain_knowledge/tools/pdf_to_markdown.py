#!/usr/bin/env python
"""Convert one or more PDFs in ../pdfs to simple markdown next to originals.

Usage:
  python pdf_to_markdown.py file1.pdf [file2.pdf ...]
  python pdf_to_markdown.py --all            # convert all PDFs without existing non-placeholder .converted.md

Rules:
  - Never overwrite an existing non-placeholder converted file.
  - If a placeholder (contains the string 'Conversion pending.') exists, replace it.
  - Output filename: <stem>.converted.md in the same pdfs directory (legacy convention).
  - Minimal cleanup: collapse >2 blank lines, trim trailing spaces.

Dependencies: pdfminer.six (declared in requirements.txt)
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
from typing import List
from pdfminer.high_level import extract_text  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = ROOT / "pdfs"

PLACEHOLDER_MARKER = "Conversion pending. Run your PDF-to-markdown conversion tool"


def is_placeholder(md_path: Path) -> bool:
    try:
        txt = md_path.read_text(encoding="utf-8")
    except Exception:
        return False
    return PLACEHOLDER_MARKER in txt


def convert(pdf_path: Path, force_placeholder_only: bool = True) -> Path | None:
    if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
        print(f"[SKIP] Not a PDF or missing: {pdf_path}")
        return None
    out_path = pdf_path.with_suffix(".converted.md")
    if out_path.exists() and not is_placeholder(out_path):
        print(f"[KEEP] Existing converted markdown (non-placeholder): {out_path.name}")
        return out_path
    if out_path.exists() and is_placeholder(out_path):
        print(f"[REPLACE] Placeholder detected: {out_path.name}")
    try:
        raw_text = extract_text(str(pdf_path))
    except Exception as e:
        print(f"[ERROR] Extract failed {pdf_path.name}: {e}")
        return None
    # Basic cleanup
    lines = [l.rstrip() for l in raw_text.splitlines()]
    cleaned: List[str] = []
    blank = 0
    for l in lines:
        if l.strip():
            cleaned.append(l)
            blank = 0
        else:
            blank += 1
            if blank < 2:
                cleaned.append("")
    content = "\n".join(cleaned).strip() + "\n"
    header = f"# Auto-converted: {pdf_path.stem}\n\n(First-pass conversion; manual cleanup recommended.)\n\n"
    out_path.write_text(header + content, encoding="utf-8")
    print(f"[OK] Converted {pdf_path.name} -> {out_path.name}")
    return out_path


def list_pdfs(all_flag: bool, targets: List[str]) -> List[Path]:
    if targets:
        return [Path(t) if Path(t).is_absolute() else (PDF_DIR / t) for t in targets]
    if all_flag:
        return sorted(PDF_DIR.glob("*.pdf"))
    return []


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="*", help="PDF filenames (relative to pdfs dir) or absolute paths")
    ap.add_argument("--all", action="store_true", help="Convert all PDFs without non-placeholder converted output")
    args = ap.parse_args(argv)
    pdfs = list_pdfs(args.all, args.pdfs)
    if not pdfs:
        print("Provide PDF filenames or use --all")
        return 1
    count = 0
    for p in pdfs:
        res = convert(p)
        if res:
            count += 1
    print(f"Done. Converted {count} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
