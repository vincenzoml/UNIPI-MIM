from pathlib import Path
from markdown_slides_generator.core.content_splitter import ContentSplitter


def test_full_bibliography_expansion(tmp_path: Path):
    # Create a miniature bib file
    bib = tmp_path / 'mini.bib'
    bib.write_text("""@article{demo2025,\n  author={Example, Alice and Example, Bob},\n  title={Demo Reference Entry},\n  year={2025},\n  journal={Journal of Demonstrations}\n}\n""", encoding='utf-8')
    md = tmp_path / 'lecture.md'
    md.write_text("Title\n\n<!-- INSERT-BIB mini.bib -->\n", encoding='utf-8')
    splitter = ContentSplitter()
    slides, notes = splitter.split_content(str(md))
    assert '## References' in notes
    assert 'Demo Reference Entry' in slides
    assert '1.' in notes