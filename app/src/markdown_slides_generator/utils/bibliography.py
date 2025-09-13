import re
from pathlib import Path
from typing import List, Dict

BIB_ENTRY_PATTERN = re.compile(r'@(?P<type>\w+)\s*\{\s*(?P<key>[^,]+),')
FIELD_PATTERN = re.compile(r'\s*(?P<field>\w+)\s*=\s*[\"\{](?P<value>.*?)[\"\}]\s*,?\s*$')

class BibEntry:
    def __init__(self, entry_type: str, key: str, fields: Dict[str, str]):
        self.entry_type = entry_type
        self.key = key
        self.fields = fields

    def format_markdown(self, index: int) -> str:
        authors = self.fields.get('author', '').replace('\n', ' ').strip()
        year = self.fields.get('year', 'n.d.')
        title = self.fields.get('title', '').strip().rstrip('.')
        journal = self.fields.get('journal') or self.fields.get('booktitle') or self.fields.get('publisher') or ''
        howpublished = self.fields.get('howpublished', '')
        doi = self.fields.get('doi')
        url = self.fields.get('url')
        parts = []
        if authors:
            parts.append(authors)
        if year:
            parts.append(f'({year})')
        if title:
            parts.append(f'*{title}*.')
        if journal:
            parts.append(journal.rstrip('.') + '.')
        if howpublished:
            parts.append(howpublished.rstrip('.') + '.')
        if doi:
            parts.append(f'DOI: {doi}.')
        if url and not doi:
            parts.append(f'{url}')
        body = ' '.join(parts)
        return f'{index}. {body}'.strip()


def parse_bib_file(path: Path) -> List[BibEntry]:
    text = path.read_text(encoding='utf-8')
    entries: List[BibEntry] = []
    raw_entries = re.split(r'\n@', text)
    if not raw_entries:
        return entries
    first = raw_entries[0]
    if first.strip().startswith('@'):
        # First entry already has @, others need it added back
        raw_entries_processed = [first]
        raw_entries_processed += ['@' + r for r in raw_entries[1:]]
    else:
        raw_entries_processed = [first] if first.strip() else []
        raw_entries_processed += ['@' + r for r in raw_entries[1:]]
    for raw in raw_entries_processed:
        raw = raw.strip()
        if not raw:
            continue
        m = BIB_ENTRY_PATTERN.match(raw)
        if not m:
            continue
        entry_type = m.group('type')
        key = m.group('key').strip()
        body = raw[m.end():]
        fields: Dict[str, str] = {}
        # naive field parsing line by line
        for line in body.splitlines():
            line = line.strip().rstrip(',')
            if line.startswith('}'):  # end of entry
                break
            fm = FIELD_PATTERN.match(line)
            if fm:
                fields[fm.group('field').lower()] = fm.group('value').strip()
        entries.append(BibEntry(entry_type, key, fields))
    return entries


def render_bibliography_markdown(bib_path: Path) -> str:
    if not bib_path.exists():
        return f'> Bibliography file not found: {bib_path.name}'
    entries = parse_bib_file(bib_path)
    if not entries:
        return '> (No bibliography entries found)'
    lines = [e.format_markdown(i+1) for i, e in enumerate(entries)]
    header = '## References\n'
    return header + '\n'.join(lines) + '\n'
