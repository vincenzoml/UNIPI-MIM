"""
Regression test suite for common academic content patterns.

Tests for patterns that have caused issues in the past and ensures
they continue to work correctly across different versions.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from markdown_slides_generator.core.content_splitter import ContentSplitter
from markdown_slides_generator.core.quarto_orchestrator import QuartoOrchestrator
from markdown_slides_generator.batch.batch_processor import BatchProcessor
from markdown_slides_generator.config import Config


class TestRegressionPatterns:
    """Test patterns that have caused issues in previous versions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.splitter = ContentSplitter()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_nested_math_expressions(self):
        """Test nested mathematical expressions that previously caused parsing issues."""
        content = """# Complex Math

## Nested Expressions

$$\\begin{align}
f(x) &= \\sum_{n=0}^{\\infty} \\frac{f^{(n)}(a)}{n!}(x-a)^n \\\\
&= f(a) + f'(a)(x-a) + \\frac{f''(a)}{2!}(x-a)^2 + \\cdots \\\\
&= \\sum_{n=0}^{\\infty} \\frac{1}{n!} \\left[\\frac{d^n}{dx^n}f(x)\\right]_{x=a} (x-a)^n
\\end{align}$$

<!-- SLIDE -->

## Matrix Operations

$$\\mathbf{A}^{-1} = \\frac{1}{\\det(\\mathbf{A})} \\begin{pmatrix}
C_{11} & C_{21} & \\cdots & C_{n1} \\\\
C_{12} & C_{22} & \\cdots & C_{n2} \\\\
\\vdots & \\vdots & \\ddots & \\vdots \\\\
C_{1n} & C_{2n} & \\cdots & C_{nn}
\\end{pmatrix}$$

Where $C_{ij} = (-1)^{i+j} M_{ij}$ and $M_{ij}$ is the $(i,j)$ minor.

<!-- NOTES-ONLY -->

**Detailed Calculation:**

For a $2 \\times 2$ matrix:
$$\\mathbf{A} = \\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}$$

The inverse is:
$$\\mathbf{A}^{-1} = \\frac{1}{ad-bc} \\begin{pmatrix} d & -b \\\\ -c & a \\end{pmatrix}$$

This formula breaks down when $\\det(\\mathbf{A}) = ad - bc = 0$.

<!-- ALL -->
"""
        
        result = self.splitter.process_directives(content)
        
        # Should handle nested math without errors
        assert "\\begin{align}" in result["slides"]
        assert "\\begin{align}" in result["notes"]
        assert "\\begin{pmatrix}" in result["slides"]
        
        # Notes-only content should be separated
        assert "Detailed Calculation" in result["notes"]
        assert "Detailed Calculation" not in result["slides"]
        
        # LaTeX validation should pass
        latex_result = self.splitter.get_latex_validation_result()
        assert latex_result is not None
    
    def test_code_blocks_with_directives(self):
        """Test code blocks containing directive-like comments."""
        content = """# Code Examples

## HTML Generation

```python
def generate_html():
    html = '''
    <html>
    <!-- This is an HTML comment, not a directive -->
    <body>
        <!-- SLIDE --> 
        <h1>Title</h1>
        <!-- NOTES-ONLY -->
        <p>This should not be parsed as directives</p>
    </body>
    </html>
    '''
    return html
```

<!-- SLIDE -->

## JavaScript Code

```javascript
// Function to handle slides
function processSlides() {
    // <!-- SLIDE-ONLY --> - this is just a comment
    console.log("Processing slides");
    
    /* 
     * <!-- ALL --> - this should also be ignored
     * Multi-line comment
     */
    return true;
}
```

<!-- NOTES-ONLY -->

**Important Note:** The directive-like comments inside code blocks should NOT be processed as actual directives. They are part of the code content.

<!-- ALL -->

## Real Directive

This content should be in both slides and notes.
"""
        
        result = self.splitter.process_directives(content)
        
        # Code blocks should be preserved intact
        assert "<!-- This is an HTML comment, not a directive -->" in result["slides"]
        assert "<!-- SLIDE -->" in result["slides"]  # Inside code block
        assert "// <!-- SLIDE-ONLY --> - this is just a comment" in result["slides"]
        
        # Real directives should work
        assert "Important Note" in result["notes"]
        assert "Important Note" not in result["slides"]
        assert "This content should be in both" in result["slides"]
        assert "This content should be in both" in result["notes"]
        
        # Should only find the real directives, not the ones in code
        directives = self.splitter.parser.parse_directives(content)
        real_directives = [d for d in directives if d.line_number not in [8, 9, 10, 25, 29]]
        assert len(real_directives) == 3  # SLIDE, NOTES-ONLY, ALL
    
    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters."""
        content = """# Unicode Content

## Mathematical Symbols

Greek letters: α, β, γ, δ, ε, ζ, η, θ, ι, κ, λ, μ, ν, ξ, ο, π, ρ, σ, τ, υ, φ, χ, ψ, ω

Mathematical operators: ∀, ∃, ∈, ∉, ⊂, ⊃, ∩, ∪, ∧, ∨, ¬, →, ↔, ≡, ≠, ≤, ≥, ±, ∞

<!-- SLIDE -->

## International Content

**Français:** Les caractères accentués comme é, è, à, ç, ù doivent être préservés.

**Español:** Los caracteres especiales como ñ, ü, ¿, ¡ son importantes.

**Deutsch:** Umlaute wie ä, ö, ü und ß müssen korrekt behandelt werden.

**中文:** 中文字符应该正确处理，包括标点符号：，。！？

**العربية:** النص العربي يجب أن يُعرض بشكل صحيح من اليمين إلى اليسار.

**Русский:** Кириллические символы должны корректно обрабатываться.

<!-- NOTES-ONLY -->

**Technical Notes:**

When processing international content, ensure:
1. UTF-8 encoding is maintained throughout the pipeline
2. Right-to-left languages are handled correctly
3. Combining characters and diacritics are preserved
4. Mathematical Unicode symbols are distinguished from text

<!-- ALL -->

## Emoji and Symbols

Emojis: 🔬 📊 📈 📉 💡 🎯 ✅ ❌ ⚠️ 📝 📚 🧮

Arrows: ← → ↑ ↓ ↔ ↕ ↖ ↗ ↘ ↙ ⇐ ⇒ ⇔

Currency: $ € £ ¥ ₹ ₽ ₩ ₪ ₫ ₡

Mathematical: ∑ ∏ ∫ ∮ √ ∛ ∜ ∂ ∇ ∆ ∞ ∝ ∴ ∵
"""
        
        result = self.splitter.process_directives(content)
        
        # Unicode characters should be preserved
        assert "α, β, γ, δ" in result["slides"]
        assert "∀, ∃, ∈, ∉" in result["slides"]
        
        # International text should be preserved
        assert "Les caractères accentués" in result["slides"]
        assert "Los caracteres especiales" in result["slides"]
        assert "中文字符应该正确处理" in result["slides"]
        assert "النص العربي" in result["slides"]
        assert "Кириллические символы" in result["slides"]
        
        # Technical notes should be in notes only
        assert "Technical Notes" in result["notes"]
        assert "UTF-8 encoding" in result["notes"]
        assert "Technical Notes" not in result["slides"]
        
        # Emojis and symbols should be preserved
        assert "🔬 📊 📈" in result["slides"]
        assert "← → ↑ ↓" in result["slides"]
        assert "$ € £ ¥" in result["slides"]
    
    def test_deeply_nested_lists(self):
        """Test deeply nested list structures."""
        content = """# Nested Lists

## Complex Hierarchy

1. **First Level**
   - Sub-item A
     - Sub-sub-item 1
       - Sub-sub-sub-item α
         - Deep nesting level 1
           - Deep nesting level 2
             - Deep nesting level 3
               - Deep nesting level 4
                 - Deep nesting level 5
   - Sub-item B
     1. Numbered sub-item 1
        a. Letter sub-item a
           i. Roman numeral i
              - Mixed bullet point
                * Different bullet style
                  + Another bullet style
     2. Numbered sub-item 2

2. **Second Level**
   - Another structure
     - With different patterns

<!-- SLIDE -->

## Mixed List Types

- **Bullet List**
  1. **Numbered inside bullet**
     - Bullet inside numbered
       a. Letter inside bullet inside numbered
          - Another bullet
            1. Number inside bullet inside letter
               - Deep bullet
  2. **Another numbered**
     - More bullets

<!-- NOTES-ONLY -->

**Formatting Notes:**

Complex nested lists can be challenging for different output formats:

1. **HTML/reveal.js:** Generally handles nesting well
2. **LaTeX/Beamer:** May need custom list environments for deep nesting
3. **PowerPoint:** Limited nesting support, may flatten deep structures

**Best Practices:**
- Limit nesting to 4-5 levels maximum
- Use consistent indentation (2-4 spaces per level)
- Consider breaking very deep lists into separate slides
- Test output in target format to ensure readability

<!-- ALL -->

## Definition Lists

Term 1
: Definition of term 1 with detailed explanation that may span multiple lines and include various formatting elements.

Term 2
: Short definition.

Complex Term with **formatting**
: Definition that includes:
  - Bullet points
  - **Bold text**
  - *Italic text*
  - `Code snippets`
  - Mathematical expressions: $f(x) = x^2$

Nested Term
: Definition with nested structure:
  
  Sub-term A
  : Sub-definition A
  
  Sub-term B
  : Sub-definition B with more content
"""
        
        result = self.splitter.process_directives(content)
        
        # Nested lists should be preserved
        assert "Deep nesting level 5" in result["slides"]
        assert "Roman numeral i" in result["slides"]
        assert "Different bullet style" in result["slides"]
        
        # Mixed list types should work
        assert "Number inside bullet inside letter" in result["slides"]
        
        # Definition lists should be preserved
        assert "Term 1" in result["slides"]
        assert ": Definition of term 1" in result["slides"]
        assert "Complex Term with **formatting**" in result["slides"]
        
        # Notes-only formatting advice
        assert "Formatting Notes" in result["notes"]
        assert "Best Practices" in result["notes"]
        assert "Formatting Notes" not in result["slides"]
    
    def test_table_edge_cases(self):
        """Test complex table structures that have caused issues."""
        content = """# Complex Tables

## Table with Math and Code

| Algorithm | Time Complexity | Space Complexity | Implementation |
|-----------|-----------------|------------------|----------------|
| Bubble Sort | $O(n^2)$ | $O(1)$ | `bubble_sort()` |
| Quick Sort | $O(n \\log n)$ avg<br/>$O(n^2)$ worst | $O(\\log n)$ | `quick_sort()` |
| Merge Sort | $O(n \\log n)$ | $O(n)$ | `merge_sort()` |
| Heap Sort | $O(n \\log n)$ | $O(1)$ | `heap_sort()` |

<!-- SLIDE -->

## Table with Unicode and Special Characters

| Language | Hello | Goodbye | Numbers |
|----------|-------|---------|---------|
| English | Hello | Goodbye | 1, 2, 3 |
| Français | Bonjour | Au revoir | un, deux, trois |
| Español | Hola | Adiós | uno, dos, tres |
| Deutsch | Hallo | Auf Wiedersehen | eins, zwei, drei |
| 中文 | 你好 | 再见 | 一, 二, 三 |
| العربية | مرحبا | وداعا | واحد، اثنان، ثلاثة |
| Русский | Привет | До свидания | один, два, три |

<!-- NOTES-ONLY -->

**Table Formatting Considerations:**

Different output formats handle tables differently:

1. **HTML/reveal.js:**
   - Full CSS styling support
   - Responsive design possible
   - Can handle complex content

2. **LaTeX/Beamer:**
   - May need `longtable` for long tables
   - Math expressions render natively
   - Limited styling options

3. **PowerPoint:**
   - Basic table support
   - May not preserve all formatting
   - Consider simplifying for PPTX output

**Best Practices:**
- Keep tables reasonably sized for slides
- Use clear, concise headers
- Consider splitting large tables across multiple slides
- Test math rendering in tables across formats

<!-- ALL -->

## Table with Alignment and Formatting

| Left Aligned | Center Aligned | Right Aligned | Mixed Content |
|:-------------|:--------------:|--------------:|:--------------|
| This text is left-aligned | This is centered | This is right-aligned | **Bold** text |
| Short | Medium length text | Very long text that might wrap | *Italic* text |
| `code` | $\\sum_{i=1}^n i$ | 123.456 | [Link](http://example.com) |
| • Bullet | ✓ Checkmark | → Arrow | 🔬 Emoji |

## Nested Table Content

| Feature | Description | Example |
|---------|-------------|---------|
| Lists in cells | You can include:<br/>• Bullet points<br/>• Multiple items<br/>• In table cells | • Item 1<br/>• Item 2 |
| Code blocks | Inline code: `function()`<br/>Or code snippets | `def hello():`<br/>`    print("Hi")` |
| Math expressions | Both inline $E=mc^2$ and<br/>display math work | $\\int_0^1 x dx = \\frac{1}{2}$ |
| Images | ![Alt text](image.png)<br/>Images can be included | ![Plot](graph.png) |
"""
        
        result = self.splitter.process_directives(content)
        
        # Tables with math should be preserved
        assert "$O(n^2)$" in result["slides"]
        assert "$O(n \\log n)$" in result["slides"]
        assert "`bubble_sort()`" in result["slides"]
        
        # Unicode in tables should work
        assert "你好" in result["slides"]
        assert "مرحبا" in result["slides"]
        assert "Привет" in result["slides"]
        
        # Table alignment should be preserved
        assert ":-------------" in result["slides"]  # Left align
        assert ":--------------:" in result["slides"]  # Center align
        assert "--------------:" in result["slides"]  # Right align
        
        # Complex table content should work
        assert "• Bullet points<br/>• Multiple items" in result["slides"]
        assert "`def hello():`<br/>`    print(\"Hi\")`" in result["slides"]
        
        # Notes-only table advice
        assert "Table Formatting Considerations" in result["notes"]
        assert "Table Formatting Considerations" not in result["slides"]
    
    def test_mixed_content_edge_cases(self):
        """Test edge cases with mixed content types."""
        content = """# Mixed Content Edge Cases

## Code Block Immediately After Directive

<!-- SLIDE-ONLY -->
```python
def immediate_code():
    # This code block comes right after a directive
    return "Should work correctly"
```

## Math Immediately After Directive

<!-- NOTES-ONLY -->
$$\\begin{align}
x &= \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a} \\\\
&= \\text{quadratic formula}
\\end{align}$$

<!-- ALL -->

## List Immediately After Directive

<!-- SLIDE -->
1. First item right after directive
2. Second item
   - Nested item
   - Another nested item

## Blockquote After Directive

<!-- NOTES-ONLY -->
> This is a blockquote that comes immediately after a directive.
> It should be properly handled and included only in notes.
> 
> Multiple paragraphs in blockquotes should also work correctly.

<!-- ALL -->

## Table After Directive

<!-- SLIDE -->
| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
| Data 3   | Data 4   |

## Image After Directive

<!-- NOTES-ONLY -->
![Important Diagram](diagram.png "This diagram explains the concept")

*Figure 1: Conceptual diagram showing the relationship between variables.*

<!-- ALL -->

## Multiple Directives in Sequence

<!-- SLIDE-ONLY -->
This content is only for slides.

<!-- NOTES-ONLY -->
This content is only for notes.

<!-- ALL -->
This content is for both.

<!-- SLIDE -->
New slide boundary.

<!-- SLIDE-ONLY -->
More slide-only content.

<!-- ALL -->
Back to both again.
"""
        
        result = self.splitter.process_directives(content)
        
        # Code blocks after directives should work
        assert "def immediate_code():" in result["slides"]
        assert "def immediate_code():" not in result["notes"]
        
        # Math after directives should work
        assert "\\begin{align}" in result["notes"]
        assert "\\begin{align}" not in result["slides"]
        
        # Lists after directives should work
        assert "First item right after directive" in result["slides"]
        assert "Nested item" in result["slides"]
        
        # Blockquotes after directives should work
        assert "> This is a blockquote" in result["notes"]
        assert "> This is a blockquote" not in result["slides"]
        
        # Tables after directives should work
        assert "| Column 1 | Column 2 |" in result["slides"]
        
        # Images after directives should work
        assert "![Important Diagram]" in result["notes"]
        assert "![Important Diagram]" not in result["slides"]
        
        # Multiple sequential directives should work
        assert "This content is only for slides" in result["slides"]
        assert "This content is only for slides" not in result["notes"]
        assert "This content is only for notes" in result["notes"]
        assert "This content is only for notes" not in result["slides"]
        assert "This content is for both" in result["slides"]
        assert "This content is for both" in result["notes"]


class TestOutputQualityRegression:
    """Test output quality standards that must be maintained."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.splitter = ContentSplitter()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_yaml_frontmatter_quality(self):
        """Test that generated YAML frontmatter meets quality standards."""
        content = """# Test Lecture

This is test content for YAML generation.

<!-- SLIDE -->

## Section 1

Content here.
"""
        
        input_file = self.temp_path / "test.md"
        input_file.write_text(content)
        
        slides_path, notes_path = self.splitter.generate_quarto_files(
            str(input_file),
            str(self.temp_path / "output")
        )
        
        # Check slides YAML quality
        slides_content = Path(slides_path).read_text()
        assert slides_content.startswith("---\n")
        
        # Extract YAML section
        yaml_end = slides_content.find("---\n", 4)
        yaml_section = slides_content[4:yaml_end]
        
        # Parse YAML to ensure it's valid
        import yaml
        slides_config = yaml.safe_load(yaml_section)
        
        # Quality checks for slides
        assert 'title' in slides_config
        assert 'format' in slides_config
        assert 'revealjs' in slides_config['format']
        assert slides_config['format']['revealjs']['theme'] == 'white'
        assert slides_config['format']['revealjs']['slide-number'] is True
        
        # Check notes YAML quality
        notes_content = Path(notes_path).read_text()
        yaml_end = notes_content.find("---\n", 4)
        yaml_section = notes_content[4:yaml_end]
        notes_config = yaml.safe_load(yaml_section)
        
        # Quality checks for notes
        assert 'title' in notes_config
        assert 'Lecture Notes' in notes_config['title']
        assert 'format' in notes_config
        assert 'pdf' in notes_config['format']
        assert notes_config['format']['pdf']['toc'] is True
        assert notes_config['format']['pdf']['number-sections'] is True
    
    def test_content_preservation_quality(self):
        """Test that content is preserved without corruption."""
        original_content = """# Original Content

This content should be preserved **exactly** as written.

## Mathematical Content

The equation $E = mc^2$ should remain intact.

Display math:
$$\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}$$

## Code Content

```python
def preserve_this():
    # Comments should be preserved
    return "exactly as written"
```

## Special Characters

Unicode: α, β, γ, δ
Symbols: ←, →, ↑, ↓
Emojis: 🔬, 📊, 💡

## Lists and Tables

1. First item
   - Nested item
   - Another nested

| Column | Value |
|--------|-------|
| A      | 1     |
| B      | 2     |

<!-- SLIDE -->

## Slide Content

This should appear in slides.

<!-- NOTES-ONLY -->

## Notes Content

This should appear only in notes.

<!-- ALL -->

## Both Content

This should appear in both.
"""
        
        result = self.splitter.process_directives(original_content)
        
        # Check that mathematical content is preserved exactly
        assert "$E = mc^2$" in result["slides"]
        assert "$E = mc^2$" in result["notes"]
        assert "\\int_0^\\infty e^{-x^2} dx" in result["slides"]
        
        # Check that code is preserved exactly
        assert "def preserve_this():" in result["slides"]
        assert "# Comments should be preserved" in result["slides"]
        assert 'return "exactly as written"' in result["slides"]
        
        # Check that special characters are preserved
        assert "α, β, γ, δ" in result["slides"]
        assert "←, →, ↑, ↓" in result["slides"]
        assert "🔬, 📊, 💡" in result["slides"]
        
        # Check that structure is preserved
        assert "| Column | Value |" in result["slides"]
        assert "1. First item" in result["slides"]
        assert "   - Nested item" in result["slides"]
        
        # Check directive processing
        assert "This should appear in slides" in result["slides"]
        assert "This should appear only in notes" in result["notes"]
        assert "This should appear only in notes" not in result["slides"]
        assert "This should appear in both" in result["slides"]
        assert "This should appear in both" in result["notes"]
    
    def test_academic_formatting_standards(self):
        """Test that academic formatting standards are maintained."""
        academic_content = """---
title: "Academic Standards Test"
author: "Prof. Test"
date: "2024-01-01"
---

# Academic Formatting Standards

## Citations and References

According to Smith et al. (2023), the methodology should follow established protocols [@smith2023].

See also:
- Johnson (2022) for background theory
- Williams & Brown (2021) for experimental design
- Davis et al. (2020) for statistical analysis

## Mathematical Notation

**Theorem 1.1:** For any continuous function $f: [a,b] \\to \\mathbb{R}$, there exists $c \\in (a,b)$ such that:

$$f'(c) = \\frac{f(b) - f(a)}{b - a}$$

**Proof:** By the Mean Value Theorem...

**Definition 1.2:** A sequence $(a_n)_{n=1}^\\infty$ converges to $L$ if:

$$\\forall \\varepsilon > 0, \\exists N \\in \\mathbb{N} : n \\geq N \\Rightarrow |a_n - L| < \\varepsilon$$

## Figure and Table References

As shown in Figure 1, the relationship is linear.

![Linear Relationship](figure1.png "Figure 1: Linear relationship between variables")

The results are summarized in Table 1.

| Variable | Mean | Std Dev | p-value |
|----------|------|---------|---------|
| X        | 12.3 | 2.1     | < 0.001 |
| Y        | 45.6 | 5.2     | < 0.05  |

*Table 1: Statistical summary of experimental results*

## Cross-References

See Section 2.1 for methodology details.
Refer to Equation (1.1) for the mathematical formulation.
The proof is given in Appendix A.

<!-- SLIDE -->

## Academic Slide Standards

### Key Points Format

1. **Clear hierarchy** with numbered sections
2. **Consistent notation** throughout presentation
3. **Proper citations** for all sources
4. **Figure captions** with descriptive text

### Mathematical Presentation

- Use display math for important equations
- Number equations for reference
- Define all variables clearly
- Maintain consistent notation

<!-- NOTES-ONLY -->

**Academic Writing Guidelines:**

When preparing academic content, ensure:

1. **Citation Standards:**
   - Use consistent citation style (APA, MLA, Chicago, etc.)
   - Include page numbers for direct quotes
   - Provide complete bibliographic information

2. **Mathematical Standards:**
   - Define notation before first use
   - Use standard mathematical symbols
   - Number important equations and theorems
   - Provide proofs or references for claims

3. **Figure and Table Standards:**
   - Include descriptive captions
   - Reference all figures and tables in text
   - Use high-quality, readable graphics
   - Provide data sources and methodology

4. **Cross-Reference Standards:**
   - Use consistent numbering systems
   - Provide clear section headings
   - Include page numbers in print versions
   - Use hyperlinks in digital versions

<!-- ALL -->

## Bibliography Format

### References

Davis, A., Johnson, B., & Smith, C. (2020). *Statistical Methods in Research*. Academic Press.

Johnson, D. (2022). Background theory and applications. *Journal of Academic Research*, 15(3), 123-145.

Smith, E., Williams, F., & Brown, G. (2023). Methodology and protocols. *Research Methods Quarterly*, 8(2), 67-89.

Williams, H., & Brown, I. (2021). Experimental design principles. *Experimental Science Today*, 12(4), 234-256.
"""
        
        result = self.splitter.process_directives(academic_content)
        
        # Check citation formatting is preserved
        assert "Smith et al. (2023)" in result["slides"]
        assert "[@smith2023]" in result["slides"]
        assert "Johnson (2022)" in result["slides"]
        
        # Check mathematical formatting
        assert "**Theorem 1.1:**" in result["slides"]
        assert "**Definition 1.2:**" in result["slides"]
        assert "\\forall \\varepsilon > 0" in result["slides"]
        
        # Check figure and table references
        assert "As shown in Figure 1" in result["slides"]
        assert "![Linear Relationship]" in result["slides"]
        assert "*Table 1: Statistical summary" in result["slides"]
        
        # Check cross-references
        assert "See Section 2.1" in result["slides"]
        assert "Refer to Equation (1.1)" in result["slides"]
        
        # Check academic guidelines in notes
        assert "Academic Writing Guidelines" in result["notes"]
        assert "Citation Standards" in result["notes"]
        assert "Mathematical Standards" in result["notes"]
        assert "Academic Writing Guidelines" not in result["slides"]
        
        # Check bibliography formatting
        assert "Davis, A., Johnson, B., & Smith, C. (2020)" in result["slides"]
        assert "*Journal of Academic Research*" in result["slides"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])