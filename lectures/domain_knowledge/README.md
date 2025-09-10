# Domain Knowledge Repository

This directory centralizes domain knowledge assets (papers, standards, ethical guidelines, and tooling) referenced in the course.

## Structure

- `references/` Markdown summaries and curated notes per reference.
- `pdfs/` Downloaded source PDFs (not tracked if large; consider .gitignore patterns if needed).
- `converted_markdown/` Automated PDF-to-Markdown conversions (first-pass, may need manual cleanup).
- `tools/` Utility scripts (fetching, conversion, verification).
- `requirements.txt` Additional dependencies focused on acquisition and parsing.

## Manual-First Knowledge Base Policy (PDFs Directory = Authoritative)

The knowledge base now prioritizes **manual acquisition** of source documents. Automated fetch scripts are *secondary* and may be removed or ignored. The authoritative index is `REFERENCES.md` (in this folder) which lists:

| Column | Meaning |
|--------|---------|
| Link | Canonical landing page (publisher) |
| Identifier | DOI / internal code / arXiv / IEEE number |
| Status | pending / downloaded / access_blocked / duplicate / existing |
| Notes | Free-form: open access, needs cookies, chapter PDF only, etc. |

### Rationale
1. Avoid accidental downloading of full books when only a chapter is needed (esp. Springer).
2. Respect license / access controls; manual step ensures human verification.
3. Prevent noisy proliferation of helper scripts; keep process transparent and audit-friendly.

### Minimal Manual Workflow
1. Add or update an entry row in `REFERENCES.md` (status = `pending`).
2. In a browser (institutional access if needed) open the link; for Springer choose the **Download PDF** link containing the encoded DOI with chapter suffix (`...%2F978-..._<chapter>.pdf`). Avoid links without the `_N` suffix (those are usually the full book).
3. Save the PDF locally in `pdfs/` as: `pdfs/<identifier>.pdf` (normalize: lowercase, replace `/` with `_`). The `pdfs/` directory is now the **single source of truth**.
4. (Optional) Create a companion Markdown file for quick reference **in the same directory** with the exact same stem plus the suffix `.converted.md` (e.g. `springer_chapter_978_3_030_17462_0_16.converted.md`).
5. Update `REFERENCES.md` status to `downloaded` and add any note (e.g. `open_access`, `requires_auth`).

### Naming Conventions
- Springer chapter: `springer_chapter_<doi_reencoded>.pdf` (retain underscores). Example: `springer_chapter_978_3_030_17462_0_16.pdf`.
- ScienceDirect article: `S<pii>.pdf` or meaningful slug (e.g. `artmed_S0933365725000892.pdf`).
- IEEE document: `ieee_<number>.pdf`.
- Companion converted text: `<same_stem>.converted.md` stored beside the PDF.

### Status Values
| Status | Meaning |
|--------|---------|
| pending | Identified; PDF not yet stored |
| downloaded | PDF present in `pdfs/` |
| access_blocked | Paywall / auth required (retry with institutional access) |
| duplicate | Duplicate row (keep first occurrence authoritative) |
| existing | Already present before manual list adoption |

### Chapter vs. Book (Springer)
Always choose the PDF whose URL pattern ends with `..._%5F<chapter>.pdf` (URL-encoded underscore + chapter). If a very large file (>40MB) appears, re-check you did not fetch the entire book volume.

### Open Access Check (ScienceDirect)
If the landing page displays a Creative Commons license and `View PDF` works without authentication, mark note `open_access`.

### IEEE Access
Use institutional login. After successful browser access, use *Download PDF* then save. If automated curl needed, export cookies and execute manually—do not script distribution here.

### Conversion (Optional)
Lightweight single-file conversion (example) creating adjacent `.converted.md`:
```
python - <<'EOF'
import sys, pathlib
from pdfminer.high_level import extract_text
pdf = pathlib.Path(sys.argv[1])
text = extract_text(str(pdf))
out = pdf.with_suffix('.converted.md')
out.write_text(f"# Converted (first pass) - {pdf.name}\n\n"+text, encoding='utf-8')
print('Wrote', out)
EOF pdfs/<file>.pdf
```
Edit the `.converted.md` manually; no automation should mutate existing files in `pdfs/` once committed.

### Removal of Legacy Automation
The previous `converted_markdown/` directory and `metadata.json` workflow are deprecated. Do not place new content there. The authoritative artifacts are:
- `pdfs/*.pdf` (primary sources)
- `pdfs/*.converted.md` (optional human-maintained summaries/transcriptions)
- `REFERENCES.md` (index + status)

No tool (script, CI, or external process) should delete, rename, or overwrite files under `pdfs/` without explicit human action. Treat `pdfs/` as append-only except for correcting an incorrect file (retain a backup if replaced).

### Adding a New Entry (Example)
Append to the table in `REFERENCES.md`:
```
| https://link.springer.com/chapter/10.1007/978-3-031-XXXX-Y_Z | 10.1007/978-3-031-XXXX-Y_Z | pending | chapter |
```
Then follow the workflow above.

---
Maintained alongside lecture materials; manual-first policy in effect.
