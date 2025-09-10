#!/usr/bin/env python
"""Fetch and convert reference documents based on metadata.json.

Usage:
        python fetch_references.py --all
        python fetch_references.py --slug some_reference
        python fetch_references.py --id REF1
        python fetch_references.py --slug some_reference --force

Optional configuration file (JSON): lectures/domain_knowledge/config/fetch_config.json
Example:
{
    "socks_proxy": "socks5h://proxy-host:1080",
    "download_delay_seconds": 1.0
}
Command-line flags override config values.

Features:
- DOI resolution via requests (simple redirect follow)
- PDF download to ../pdfs
- Basic integrity checks (status, length, sha256)
- PDF -> text (pdfminer), then heuristic markdown conversion
- Metadata status updates (adds file info)

Limitations:
- Some regulatory / protected documents skipped.
- Conversion quality varies; manual cleanup recommended.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
import hashlib
import socket
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import re

import requests
from urllib.parse import urljoin, unquote
from pdfminer.high_level import extract_text  # type: ignore

try:
    from markdownify import markdownify as html_to_md  # type: ignore
except Exception:  # pragma: no cover
    html_to_md = None  # fallback

ROOT = Path(__file__).resolve().parent.parent
META_PATH = ROOT / "references" / "metadata.json"
PDF_DIR = ROOT / "pdfs"
MD_CONVERTED_DIR = ROOT / "converted_markdown"
CONFIG_PATH = ROOT / "config" / "fetch_config.json"

USER_AGENT = "UNIPI-MIM-ReferenceFetcher/0.2 (+local academic use)"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.5",
}

# Simple DOI regex
DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")


def load_metadata() -> List[Dict[str, Any]]:
    with META_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_metadata(items: List[Dict[str, Any]]):
    with META_PATH.open("w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)


def resolve_doi_url(doi: str) -> str:
    return f"https://doi.org/{doi}" if not doi.lower().startswith("http") else doi


def is_pdf_bytes(data: bytes) -> bool:
    return data.startswith(b"%PDF-") and b"%%EOF" in data[-2048:]


def arxiv_direct(doi: str) -> Optional[str]:
    # arXiv DOI pattern: 10.48550/arXiv.<id>
    m = re.match(r"10\.48550/arXiv\.(\d{4}\.\d{4,5})(v\d+)?", doi)
    if not m:
        return None
    arx_id = m.group(1)
    return f"https://arxiv.org/pdf/{arx_id}.pdf"


SPRINGER_CHAPTER_RE = re.compile(r"10\.1007/978-[^_]+_\d+", re.IGNORECASE)


def is_springer_chapter_doi(doi: str) -> bool:
    return bool(SPRINGER_CHAPTER_RE.match(doi))


def scrape_springer_chapter_pdf(doi: str, session: requests.Session) -> Optional[bytes]:
    """Attempt to obtain the chapter-level PDF bytes for a Springer chapter DOI.

    Strategy:
      1. Resolve DOI (likely landing page HTML)
      2. Collect all href values containing '/content/pdf/' and ending with .pdf
      3. Prefer links whose (URL-decoded) filename contains the full DOI with encoded slash
         pattern '10.1007%2F<rest>' and ends with _<n>.pdf (chapter) rather than the base book .pdf.
      4. Fallback: choose the shortest link containing an underscore after the 978- block.
    Returns raw PDF bytes or None.
    """
    landing_url = resolve_doi_url(doi)
    try:
        r = session.get(landing_url, timeout=30, allow_redirects=True)
    except Exception as e:
        print(f"[WARN] Springer landing fetch failed {landing_url}: {e}")
        return None
    if r.status_code != 200 or not r.text:
        return None
    html = r.text
    pdf_links: List[str] = []
    for m in re.finditer(r'href=["\']([^"\']+\.pdf)"', html, re.IGNORECASE):
        href = m.group(1)
        if '/content/pdf/' in href:
            pdf_links.append(urljoin(r.url, href))
    if not pdf_links:
        return None
    # Rank links: prefer those whose decoded tail contains '_' chapter suffix matching DOI
    chapter_suffix = '_' + doi.split('_')[-1]
    def score(link: str) -> Tuple[int, int]:
        dec = unquote(link)
        # Higher primary score if exact suffix appears before .pdf
        primary = 1 if chapter_suffix + '.pdf' in dec else 0
        # Penalize longer links
        return (primary, -len(dec))
    pdf_links.sort(key=score, reverse=True)
    for link in pdf_links:
        try:
            r2 = session.get(link, timeout=40)
        except Exception as e:
            print(f"[WARN] Springer chapter pdf attempt failed {link}: {e}")
            continue
        if r2.status_code == 200 and is_pdf_bytes(r2.content):
            # Heuristic: Skip if looks like whole book (very large > 40MB)
            if len(r2.content) > 40 * 1024 * 1024:
                print(f"[INFO] Skipping very large PDF candidate (likely full book) {len(r2.content)} bytes")
                continue
            print(f"[OK] Springer chapter PDF located via scraped link")
            return r2.content
    return None


def download_pdf(doi: str, target: Path, prefer_springer_chapter: bool = False) -> Optional[Path]:
    # Special-case arXiv for reliability
    arxiv_url = arxiv_direct(doi)
    tried: List[str] = []
    candidates: List[str] = []
    if arxiv_url:
        candidates.append(arxiv_url)
    # DOI resolver last (may land on paywall/HTML)
    candidates.append(resolve_doi_url(doi))

    session = requests.Session()
    session.headers.update(HEADERS)

    # Springer chapter pre-pass
    if prefer_springer_chapter and is_springer_chapter_doi(doi):
        chapter_bytes = scrape_springer_chapter_pdf(doi, session)
        if chapter_bytes and is_pdf_bytes(chapter_bytes):
            target.write_bytes(chapter_bytes)
            size = target.stat().st_size
            print(f"[OK] PDF (Springer chapter) {doi} -> {target.name} ({size} bytes)")
            return target

    for url in candidates:
        tried.append(url)
        try:
            r = session.get(url, timeout=30, allow_redirects=True)
        except Exception as e:
            print(f"[WARN] fetch failed {url}: {e}")
            continue
        if r.status_code != 200:
            print(f"[WARN] HTTP {r.status_code} for {url}")
            continue
        data = r.content
        if is_pdf_bytes(data):
            target.write_bytes(data)
            size = target.stat().st_size
            print(f"[OK] PDF confirmed {doi} -> {target.name} ({size} bytes)")
            if size < 20_000:
                print(f"[NOTE] Small PDF; verify completeness.")
            return target
        # Attempt HTML scraping for embedded PDF link (one pass)
        text = r.text if isinstance(r.text, str) else ""
        pdf_link = None
        for line in text.splitlines():
            if ".pdf" in line.lower():
                m = re.search(r'href=["\']([^"\']+\.pdf)', line, re.IGNORECASE)
                if m:
                    pdf_link = m.group(1)
                    break
        if pdf_link:
            pdf_url = urljoin(r.url, pdf_link)
            tried.append(pdf_url)
            try:
                r2 = session.get(pdf_url, timeout=30)
                if r2.status_code == 200 and is_pdf_bytes(r2.content):
                    target.write_bytes(r2.content)
                    size = target.stat().st_size
                    print(f"[OK] PDF (scraped) {doi} -> {target.name} ({size} bytes)")
                    return target
            except Exception as e:
                print(f"[WARN] secondary PDF fetch failed {pdf_url}: {e}")
        # else continue to next candidate
    print(f"[ERROR] Failed to obtain valid PDF for {doi}. Tried: {tried}")
    return None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def pdf_to_markdown(pdf_path: Path, md_path: Path):
    # Double-check magic before extraction to avoid confusing errors
    raw = pdf_path.read_bytes()
    if not is_pdf_bytes(raw):
        print(f"[WARN] Not a valid PDF structure, skipping conversion: {pdf_path.name}")
        return
    try:
        text = extract_text(str(pdf_path))
    except Exception as e:
        print(f"[ERROR] Extract text failed {pdf_path.name}: {e}")
        return
    # Very lightweight cleanup
    lines = [l.rstrip() for l in text.splitlines()]
    # Collapse excessive blank lines
    cleaned: List[str] = []
    blank = 0
    for l in lines:
        if l.strip():
            blank = 0
            cleaned.append(l)
        else:
            blank += 1
            if blank < 2:
                cleaned.append("")
    md_content = "\n".join(cleaned)
    header = f"# Auto-converted: {pdf_path.stem}\n\n(First-pass conversion; manual edits recommended.)\n\n"
    md_path.write_text(header + md_content, encoding="utf-8")
    print(f"[OK] Converted {pdf_path.name} -> {md_path.name}")


def process_reference(ref: Dict[str, Any], force: bool, session: requests.Session, fix_springer: bool = False) -> Dict[str, Any]:
    """Download and convert a single reference.

    File naming priority: slug > id for both PDF and converted markdown.
    Existing legacy id-based files are migrated (renamed) to slug-based names if
    slug is present and no slug-named file exists yet.
    """
    doi = ref.get("doi")
    ref_id = ref.get("id")
    slug = ref.get("slug") or ref_id
    if not doi:
        print(f"[SKIP] {ref_id}: no DOI (status={ref.get('status')})")
        return ref
    # Always skip re-downloading if a PDF already exists on disk (immutability guarantee)
    existing_pdf = None
    slug_path = PDF_DIR / f"{slug}.pdf"
    legacy_path = PDF_DIR / f"{ref_id}.pdf"
    if slug_path.exists():
        existing_pdf = slug_path
    elif legacy_path.exists():
        existing_pdf = legacy_path
    if existing_pdf is not None:
        # Allow re-download for Springer chapters if fix flag set
        if fix_springer and doi and is_springer_chapter_doi(doi):
            try:
                backup_path = existing_pdf.with_suffix(existing_pdf.suffix + ".bak")
                existing_size = existing_pdf.stat().st_size
                existing_pdf.rename(backup_path)
                print(f"[INFO] Backed up existing Springer PDF ({existing_size} bytes) -> {backup_path.name}")
                existing_pdf = None  # force fresh download below
            except Exception as e:
                print(f"[WARN] Could not backup existing PDF; skipping re-download: {e}")
        if existing_pdf is not None:
            try:
                rel = str(existing_pdf.relative_to(ROOT))
                if ref.get("pdf_path") != rel:
                    ref["pdf_path"] = rel
            except Exception:
                pass
            if ref.get("pdf_sha256") is None:
                try:
                    ref["pdf_sha256"] = sha256_file(existing_pdf)
                except Exception:
                    pass
            if ref.get("pdf_bytes") is None:
                try:
                    ref["pdf_bytes"] = existing_pdf.stat().st_size
                except Exception:
                    pass
            if ref.get("status") not in {"converted", "downloaded"}:
                ref["status"] = ref.get("status") or "downloaded"
            print(f"[SKIP] {ref_id}: PDF already present ({existing_pdf.name}); no refresh performed")
            if ref.get("converted_markdown") is None:
                md_path = MD_CONVERTED_DIR / f"{slug}.md"
                if not md_path.exists():
                    pdf_to_markdown(existing_pdf, md_path)
                    if md_path.exists():
                        ref["converted_markdown"] = str(md_path.relative_to(ROOT))
                        ref["status"] = "converted"
            return ref
    PDF_DIR.mkdir(exist_ok=True)
    MD_CONVERTED_DIR.mkdir(exist_ok=True)

    # Determine target paths
    pdf_path = PDF_DIR / f"{slug}.pdf"
    legacy_pdf_path = PDF_DIR / f"{ref_id}.pdf"
    if legacy_pdf_path.exists() and not pdf_path.exists():
        try:
            legacy_pdf_path.rename(pdf_path)
            print(f"[MIGRATE] Renamed legacy {legacy_pdf_path.name} -> {pdf_path.name}")
        except Exception as e:
            print(f"[WARN] Failed to migrate legacy PDF name: {e}")

    # Force flag no longer triggers re-download (immutability); user must manually delete PDF to refresh

    prefer_springer = is_springer_chapter_doi(doi)
    downloaded = download_pdf(doi, pdf_path, prefer_springer_chapter=prefer_springer)
    if not downloaded:
        ref["status"] = "download_failed"
        return ref
    if not is_pdf_bytes(downloaded.read_bytes()):
        ref["status"] = "landing_page_saved"
        ref["note"] = "Fetched content not a PDF (likely HTML). Manual download required."
        ref["pdf_path"] = str(downloaded.relative_to(ROOT))
        ref["pdf_bytes"] = downloaded.stat().st_size
        return ref

    size = pdf_path.stat().st_size
    # Classify very small PDFs as suspect
    if size < 10_000:
        ref["status"] = "suspect_small_pdf"
        ref["note"] = (ref.get("note") or "") + " PDF size <10KB – likely incomplete; consider manual retrieval."
    else:
        ref["status"] = "downloaded"
    ref["pdf_path"] = str(pdf_path.relative_to(ROOT))
    ref["pdf_sha256"] = sha256_file(pdf_path)
    ref["pdf_bytes"] = size
    if size < 5000:
        ref["note"] = (ref.get("note") or "") + " Small PDF (<5KB) – verify it's not a landing page or truncated.".strip()

    # Convert
    md_path = MD_CONVERTED_DIR / f"{slug}.md"
    legacy_md_path = MD_CONVERTED_DIR / f"{ref_id}.md"
    if legacy_md_path.exists() and not md_path.exists():
        try:
            legacy_md_path.rename(md_path)
            print(f"[MIGRATE] Renamed legacy {legacy_md_path.name} -> {md_path.name}")
        except Exception as e:
            print(f"[WARN] Failed to migrate legacy MD name: {e}")
    pdf_to_markdown(pdf_path, md_path)
    if md_path.exists():
        ref["converted_markdown"] = str(md_path.relative_to(ROOT))
        ref["status"] = "converted"
    return ref


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return {}
            return data
        except Exception as e:
            print(f"[WARN] Failed to load config {CONFIG_PATH}: {e}")
    return {}


def port_open(host: str, port: int, timeout: float = 0.3) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def start_ssh_socks_tunnel(cfg: Dict[str, Any]) -> Optional[str]:
    """Start an SSH dynamic port forwarding tunnel if requested.

    Config keys:
      auto_start_tunnel: bool
      proxy_host: remote SSH host (also used for socks5h host if no localhost override)
      proxy_port: local dynamic port (default 1080)
      ssh_user: optional SSH username
      ssh_host: optional explicit SSH host (overrides proxy_host for ssh connection target)
      ssh_port: optional SSH port (default 22)

    Behavior:
      - If auto_start_tunnel false / missing -> no action
      - If local port already open -> assume tunnel active (idempotent)
      - Launches: ssh -f -N -D {local_port} [user@]ssh_host -p ssh_port
      - Returns constructed socks5h URL (socks5h://localhost:port) on success
    """
    if not cfg.get("auto_start_tunnel"):
        return None
    local_port = int(cfg.get("proxy_port", 1080))
    ssh_host = cfg.get("ssh_host") or cfg.get("proxy_host")
    if not ssh_host:
        print("[WARN] auto_start_tunnel enabled but no ssh_host/proxy_host provided")
        return None
    ssh_user = cfg.get("ssh_user")
    ssh_port = int(cfg.get("ssh_port", 22))
    # If port already listening consider tunnel present
    if port_open("127.0.0.1", local_port):
        return f"socks5h://localhost:{local_port}"
    # Build SSH command
    target = f"{ssh_user}@{ssh_host}" if ssh_user else ssh_host
    cmd = [
        "ssh",
        "-f",  # go to background after auth
        "-N",  # no remote command
        "-D", f"{local_port}",
        "-p", str(ssh_port),
        target,
    ]
    try:
        print(f"[INFO] Starting SSH SOCKS tunnel: {' '.join(cmd)}")
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
        if res.returncode != 0:
            print(f"[WARN] ssh tunnel failed (code {res.returncode}): {res.stderr.strip()}")
            return None
        # Brief wait for port to open
        for _ in range(10):
            if port_open("127.0.0.1", local_port):
                print(f"[INFO] SSH tunnel active on localhost:{local_port}")
                return f"socks5h://localhost:{local_port}"
            time.sleep(0.2)
        print("[WARN] SSH tunnel command executed but port not open")
    except Exception as e:
        print(f"[WARN] Exception launching ssh tunnel: {e}")
    return None


def main():
    parser = argparse.ArgumentParser(description="Fetch and convert references")
    parser.add_argument("--all", action="store_true", help="Process all references")
    parser.add_argument("--id", help="Specific reference ID", default=None)
    parser.add_argument("--slug", help="Lookup by slug field", default=None)
    parser.add_argument("--force", action="store_true", help="Force re-download and reconvert")
    parser.add_argument("--fix-springer-chapters", action="store_true", help="Re-download Springer chapters (backs up existing PDFs) and prefer chapter PDFs over full book volumes")
    parser.add_argument("--retry-suspect", action="store_true", help="Attempt re-download for entries marked suspect_small_pdf by temporarily backing up existing PDF")
    parser.add_argument("--socks", help="SOCKS proxy (e.g., socks5h://host:port)")
    parser.add_argument("--config", help="Path to alternate config JSON", default=None)
    parser.add_argument("--delay", type=float, help="Download delay seconds (override)")
    args = parser.parse_args()

    items = load_metadata()
    cfg = load_config() if args.config is None else (json.load(open(args.config)) if Path(args.config).exists() else {})
    # Apply config-driven defaults
    socks_cfg = cfg.get("socks_proxy")
    # Auto-start tunnel first (may override socks config to localhost)
    tunnel_url = start_ssh_socks_tunnel(cfg)
    if tunnel_url:
        socks_cfg = tunnel_url
    # Else allow shorthand: proxy_host + optional proxy_port to construct socks5h URL
    if not socks_cfg and cfg.get("proxy_host"):
        host = cfg.get("proxy_host")
        port = cfg.get("proxy_port", 1080)
        if host:
            socks_cfg = f"socks5h://{host}:{port}"
    delay = cfg.get("download_delay_seconds", 1.0)
    if args.delay is not None:
        delay = args.delay
    if args.socks:
        socks_cfg = args.socks
    changed = False

    # Build lookup by slug if present
    slug_map = {r.get("slug"): r for r in items if r.get("slug")}
    targets: List[Dict[str, Any]] = items
    if args.slug:
        ref = slug_map.get(args.slug)
        if not ref:
            print(f"No reference with slug {args.slug}")
            return 1
        targets = [ref]
    elif args.id:
        targets = [r for r in items if r.get("id") == args.id]
        if not targets:
            print(f"No reference with id {args.id}")
            return 1
    elif not args.all:
        print("Specify --all or --id REFID or --slug SLUG")
        return 1

    # Session for potential proxy
    if socks_cfg:
        os.environ['ALL_PROXY'] = socks_cfg
        os.environ['all_proxy'] = socks_cfg
        print(f"[INFO] Using SOCKS proxy (from {'arg' if args.socks else 'config'})")

    session = requests.Session()
    session.headers.update(HEADERS)

    for ref in targets:
        if ref.get("status") == "suspect_small_pdf" and args.retry_suspect:
            # Backup existing small pdf to allow fresh attempt
            existing = ref.get("pdf_path")
            if existing:
                existing_path = ROOT / existing
                if existing_path.exists():
                    backup_path = existing_path.with_suffix(existing_path.suffix + ".bak")
                    try:
                        existing_path.rename(backup_path)
                        print(f"[INFO] Backed up suspect PDF -> {backup_path.name}")
                    except Exception as e:
                        print(f"[WARN] Could not backup suspect PDF {existing_path.name}: {e}")
            # Reset status to enable processing
            ref["status"] = "pending_download"
        if ref.get("status") in {"manual_acquisition", "external_link_only", "awaiting_metadata", "curation_pending", "partially_curated"} and not args.force:
            print(f"[SKIP] {ref['id']}: status={ref['status']}")
            continue
        updated = process_reference(ref, args.force, session, fix_springer=args.fix_springer_chapters)
        if updated is not ref:
            ref.update(updated)
        changed = True
    time.sleep(delay)

    if changed:
        save_metadata(items)
        print("[INFO] Metadata updated")
    else:
        print("[INFO] No changes")
    return 0

if __name__ == "__main__":
    sys.exit(main())
