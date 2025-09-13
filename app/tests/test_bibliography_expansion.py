from pathlib import Path
from markdown_slides_generator.core.content_splitter import ContentSplitter


def test_bibliography_expansion(tmp_path: Path):
    bib = tmp_path / 'test_refs.bib'
    bib.write_text("""@article{test2025,\n  author={Doe, Jane and Roe, Richard},\n  title={An Example Paper},\n  year={2025},\n  journal={Journal of Examples}\n}\n""", encoding='utf-8')
    md = tmp_path / 'sample.md'
    md.write_text("Intro text.\n\n<!-- INSERT-BIB test_refs.bib -->\n\nEnd.", encoding='utf-8')
    splitter = ContentSplitter()
    slides, notes = splitter.split_content(str(md))
    assert '## References' in slides
    assert 'An Example Paper' in notes
    assert '1.' in notes