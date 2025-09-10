#!/usr/bin/env python
"""Audit reference metadata for PDF completeness and anomalies.

Usage:
  python audit_references.py

Outputs a tabular summary:
  ID  DOI?  Status  PDF?  Bytes  Flags

Flags meanings:
  MISSING_PDF   metadata claims path but file absent
  NO_PDF_PATH   no pdf_path field where status implies needed
  ZERO_BYTES    file size 0
  TINY_PDF      size < 10KB (likely placeholder)
  PLACEHOLDER   status suggests awaiting / manual / external link
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any

ROOT = Path(__file__).resolve().parent.parent
META_PATH = ROOT / "references" / "metadata.json"
PDF_ROOT = ROOT / "pdfs"

NEEDS_PDF_STATUSES = {"downloaded", "converted", "suspect_small_pdf", "download_failed"}
PLACEHOLDER_STATUSES = {"awaiting_metadata", "manual_acquisition", "external_link_only", "partially_curated"}

def load_meta() -> List[Dict[str, Any]]:
    return json.loads(META_PATH.read_text(encoding="utf-8"))


def inspect(ref: Dict[str, Any]) -> Dict[str, Any]:
    pdf_path = ref.get("pdf_path")
    status = ref.get("status") or ""
    flags: List[str] = []
    size = None
    exists = False
    if pdf_path:
        f = ROOT / pdf_path
        if f.exists():
            exists = True
            size = f.stat().st_size
            if size == 0:
                flags.append("ZERO_BYTES")
            elif size < 10_000:
                flags.append("TINY_PDF")
        else:
            flags.append("MISSING_PDF")
    else:
        if status in NEEDS_PDF_STATUSES:
            flags.append("NO_PDF_PATH")
    if status in PLACEHOLDER_STATUSES:
        flags.append("PLACEHOLDER")
    return {
        "id": ref.get("id"),
        "doi": bool(ref.get("doi")),
        "status": status,
        "pdf": exists,
        "bytes": size,
        "flags": flags,
    }


def main():
    rows = [inspect(r) for r in load_meta()]
    # Column widths
    print(f"{'ID':<6} {'DOI':<4} {'STATUS':<22} {'PDF':<4} {'BYTES':>10}  FLAGS")
    for r in rows:
        b = "" if r['bytes'] is None else str(r['bytes'])
        print(f"{r['id']:<6} {str(r['doi']):<4} {r['status']:<22} {str(r['pdf']):<4} {b:>10}  {','.join(r['flags'])}")
    # Summary counts
    missing = [r for r in rows if 'MISSING_PDF' in r['flags'] or 'NO_PDF_PATH' in r['flags']]
    tiny = [r for r in rows if 'TINY_PDF' in r['flags']]
    print("\nSummary:")
    print(f"Total refs: {len(rows)}")
    print(f"Need attention (missing path/file): {len(missing)} -> {[r['id'] for r in missing]}")
    print(f"Tiny PDFs (<10KB): {len(tiny)} -> {[r['id'] for r in tiny]}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
