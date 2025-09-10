#!/usr/bin/env python
"""Fetch BibTeX for all references with a DOI and maintain references.bib.

Usage:
  python fetch_bibtex.py            # fetch/update all
  python fetch_bibtex.py --slug X   # only one
  python fetch_bibtex.py --write-missing-placeholders  # add placeholder entries where DOI missing

Logic:
  * Content negotiation via https://doi.org/<doi> Accept: application/x-bibtex
  * Stores aggregated output in references/references.bib
  * Each entry preceded by comment referencing slug & id
  * Skips already cached entries unless --force
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import re
import requests
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parent.parent
META_PATH = ROOT / "references" / "metadata.json"
BIB_PATH = ROOT / "references" / "references.bib"
CONFIG_PATH = ROOT / "config" / "fetch_config.json"
USER_AGENT = "UNIPI-MIM-BibFetcher/0.1 (+local academic use)"

def load_metadata() -> List[Dict[str, Any]]:
    with META_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)

def save_metadata(items: List[Dict[str, Any]]):
    with META_PATH.open('w', encoding='utf-8') as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

def doi_to_bib(doi: str) -> str | None:
    url = f"https://doi.org/{doi}" if not doi.lower().startswith("http") else doi
    headers = {"Accept": "application/x-bibtex; charset=utf-8", "User-Agent": USER_AGENT}
    try:
        r = requests.get(url, headers=headers, timeout=25, allow_redirects=True)
    except Exception as e:
        print(f"[WARN] DOI request failed {doi}: {e}")
        return None
    if r.status_code != 200:
        print(f"[WARN] DOI {doi} returned HTTP {r.status_code}")
        return None
    text = r.text.strip()
    if not text.startswith('@'):
        print(f"[WARN] Unexpected BibTeX content for {doi} (missing '@')")
        return None
    return text

def parse_bib_key(bib: str) -> str | None:
    m = re.match(r'@\w+{([^,]+),', bib)
    return m.group(1) if m else None

def build_index(existing: str) -> Dict[str, str]:
    idx: Dict[str, str] = {}
    for entry in existing.split('\n@')[1:]:
        # reconstruct '@' prefix
        block = '@' + entry
        key = parse_bib_key(block)
        if key:
            idx[key] = block
    return idx

def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open('r', encoding='utf-8') as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception as e:
            print(f"[WARN] Failed to load config: {e}")
    return {}


def port_open(host: str, port: int, timeout: float = 0.3) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def start_ssh_socks_tunnel(cfg: Dict[str, Any]) -> Optional[str]:
    if not cfg.get("auto_start_tunnel"):
        return None
    local_port = int(cfg.get("proxy_port", 1080))
    ssh_host = cfg.get("ssh_host") or cfg.get("proxy_host")
    if not ssh_host:
        print("[WARN] auto_start_tunnel enabled but no ssh_host/proxy_host provided")
        return None
    ssh_user = cfg.get("ssh_user")
    ssh_port = int(cfg.get("ssh_port", 22))
    if port_open("127.0.0.1", local_port):
        return f"socks5h://localhost:{local_port}"
    target = f"{ssh_user}@{ssh_host}" if ssh_user else ssh_host
    cmd = ["ssh", "-f", "-N", "-D", f"{local_port}", "-p", str(ssh_port), target]
    try:
        print(f"[INFO] Starting SSH SOCKS tunnel (BibTeX): {' '.join(cmd)}")
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
        if res.returncode != 0:
            print(f"[WARN] ssh tunnel failed (code {res.returncode}): {res.stderr.strip()}")
            return None
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
    ap = argparse.ArgumentParser()
    ap.add_argument('--slug')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--write-missing-placeholders', action='store_true', help='Add placeholder BibTeX entries for items without DOIs')
    args = ap.parse_args()

    items = load_metadata()
    cfg = load_config()
    socks_cfg = cfg.get("socks_proxy")
    tunnel_url = start_ssh_socks_tunnel(cfg)
    if tunnel_url:
        socks_cfg = tunnel_url
    if not socks_cfg and cfg.get("proxy_host"):
        host = cfg.get("proxy_host")
        port = cfg.get("proxy_port", 1080)
        if host:
            socks_cfg = f"socks5h://{host}:{port}"
    if socks_cfg:
        os.environ['ALL_PROXY'] = socks_cfg
        os.environ['all_proxy'] = socks_cfg
        print("[INFO] Using SOCKS proxy (config) for BibTeX fetch")
    slug_filter = {args.slug} if args.slug else None

    existing_text = BIB_PATH.read_text(encoding='utf-8') if BIB_PATH.exists() else ''
    index = build_index(existing_text)
    output_entries: List[str] = []
    # Preserve order: existing keys first (to keep manual edits), then new
    preserved_keys = []
    for key, block in index.items():
        preserved_keys.append(key)
        output_entries.append(block.strip())

    updated = False
    for ref in items:
        slug = ref.get('slug') or ref.get('id')
        if slug_filter and slug not in slug_filter:
            continue
        doi = ref.get('doi')
        if not doi:
            if args.write_missing_placeholders:
                key = slug
                if key not in index:
                    placeholder = f"@misc{{{key},\n  title={{ {ref.get('title','')} }},\n  note={{ Placeholder – no DOI available }},\n  year={{ {ref.get('year','')} }},\n}}"
                    output_entries.append(placeholder)
                    updated = True
            continue
        # Attempt fetch if not already present or force
        key = slug
        if key in index and not args.force:
            continue
        bib = doi_to_bib(doi)
        if not bib:
            continue
        # Replace BibTeX key with slug for stability
        bib = re.sub(r'@([a-zA-Z]+){[^,]+,', lambda m: f"@{m.group(1)}{{{key},", bib, count=1)
        output_entries.append(bib.strip())
        updated = True

    if updated or not BIB_PATH.exists():
        content = '\n\n'.join(output_entries).strip() + '\n'
        BIB_PATH.write_text(content, encoding='utf-8')
        print(f"[INFO] Wrote {BIB_PATH} ({len(output_entries)} entries)")
    else:
        print("[INFO] No BibTeX changes")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
