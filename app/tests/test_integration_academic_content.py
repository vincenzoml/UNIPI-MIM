"""
Integration tests with real academic content.

Tests the system with actual lecture markdown files including complex math,
code examples, academic formatting, and various content patterns found in
real educational materials.
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


class TestRealAcademicContent:
    """Test with realistic academic lecture content."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.splitter = ContentSplitter()
        self.orchestrator = QuartoOrchestrator()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_computer_science_lecture(self):
        """Test with computer science lecture content."""
        cs_lecture = """---
title: "Data Structures and Algorithms - Lecture 8"
author: "Prof. Computer Science"
date: "2024-02-15"
institute: "University of Technology"
course: "CS 201"
---

# Binary Search Trees

## Learning Objectives

By the end of this lecture, you will be able to:
- Understand the properties of binary search trees
- Implement BST operations (insert, search, delete)
- Analyze time complexity of BST operations
- Compare BSTs with other data structures

<!-- SLIDE -->

## BST Definition

A **Binary Search Tree** is a binary tree where:

1. Each node has at most two children
2. For every node $n$:
   - All values in left subtree ≤ $n.value$
   - All values in right subtree > $n.value$
3. Both subtrees are also BSTs

### Visual Example

```
       8
      / \\
     3   10
    / \\    \\
   1   6    14
      / \\   /
     4   7 13
```

<!-- NOTES-ONLY -->

**Important Notes for Students:**

The BST property is crucial for efficient operations. This invariant must be maintained after every modification. Students often struggle with the strict inequality - remember that duplicate values typically go to the left subtree by convention, though implementations may vary.

The visual example shows a valid BST. Notice how:
- 3 < 8, and all nodes in left subtree (1, 3, 4, 6, 7) ≤ 8
- 10 > 8, and all nodes in right subtree (10, 13, 14) > 8
- Each subtree maintains the BST property recursively

<!-- ALL -->

<!-- SLIDE -->

## BST Operations

### Search Operation

```python
def search(root, key):
    # Base case: empty tree or key found
    if root is None or root.val == key:
        return root
    
    # Key is smaller, search left subtree
    if key < root.val:
        return search(root.left, key)
    
    # Key is larger, search right subtree
    return search(root.right, key)
```

**Time Complexity:** $O(h)$ where $h$ is tree height
- Best case: $O(\\log n)$ for balanced tree
- Worst case: $O(n)$ for skewed tree

<!-- NOTES-ONLY -->

**Implementation Details:**

The recursive implementation is elegant but uses $O(h)$ stack space. An iterative version would use $O(1)$ space:

```python
def search_iterative(root, key):
    current = root
    while current is not None:
        if key == current.val:
            return current
        elif key < current.val:
            current = current.left
        else:
            current = current.right
    return None
```

Students should understand both approaches. The recursive version is more intuitive and matches the tree's recursive structure, while the iterative version is more space-efficient.

<!-- ALL -->

<!-- SLIDE -->

### Insert Operation

```python
def insert(root, key):
    # Base case: create new node
    if root is None:
        return TreeNode(key)
    
    # Recursive case: insert in appropriate subtree
    if key <= root.val:
        root.left = insert(root.left, key)
    else:
        root.right = insert(root.right, key)
    
    return root
```

### Delete Operation (Complex!)

Three cases to handle:
1. **Leaf node:** Simply remove
2. **One child:** Replace with child
3. **Two children:** Replace with inorder successor

<!-- NOTES-ONLY -->

**Delete Operation - Detailed Analysis:**

The delete operation is the most complex BST operation. Let's examine each case:

**Case 1: Leaf Node**
```python
if root.left is None and root.right is None:
    return None
```

**Case 2: One Child**
```python
if root.left is None:
    return root.right
if root.right is None:
    return root.left
```

**Case 3: Two Children**
This is the tricky case. We need to maintain the BST property. The inorder successor (smallest value in right subtree) is the perfect replacement because:
- It's larger than all values in the left subtree
- It's smaller than all other values in the right subtree

```python
def find_min(node):
    while node.left is not None:
        node = node.left
    return node

# In delete function for two children case:
successor = find_min(root.right)
root.val = successor.val
root.right = delete(root.right, successor.val)
```

Alternative: Use inorder predecessor (largest value in left subtree).

<!-- ALL -->

## Time Complexity Analysis

| Operation | Average Case | Worst Case | Best Case |
|-----------|--------------|------------|-----------|
| Search    | $O(\\log n)$ | $O(n)$     | $O(1)$    |
| Insert    | $O(\\log n)$ | $O(n)$     | $O(1)$    |
| Delete    | $O(\\log n)$ | $O(n)$     | $O(1)$    |

### Why the Variation?

- **Best case:** Balanced tree, height = $\\log_2 n$
- **Worst case:** Skewed tree (essentially a linked list), height = $n$
- **Average case:** Random insertions tend to create reasonably balanced trees

<!-- SLIDE -->

## BST vs Other Data Structures

| Structure | Search | Insert | Delete | Space |
|-----------|--------|--------|--------|-------|
| Array (unsorted) | $O(n)$ | $O(1)$ | $O(n)$ | $O(n)$ |
| Array (sorted) | $O(\\log n)$ | $O(n)$ | $O(n)$ | $O(n)$ |
| Linked List | $O(n)$ | $O(1)$ | $O(n)$ | $O(n)$ |
| Hash Table | $O(1)^*$ | $O(1)^*$ | $O(1)^*$ | $O(n)$ |
| **BST** | $O(\\log n)^*$ | $O(\\log n)^*$ | $O(\\log n)^*$ | $O(n)$ |

*Average case, assuming good hash function or balanced tree

### When to Use BSTs?

- Need sorted order traversal
- Range queries (find all values between $x$ and $y$)
- Dynamic data with frequent insertions/deletions
- Don't need constant-time operations of hash tables

<!-- NOTES-ONLY -->

**Practical Considerations:**

In practice, self-balancing BSTs (AVL trees, Red-Black trees) are preferred over basic BSTs because they guarantee $O(\\log n)$ operations. The C++ `std::map` and Java `TreeMap` use Red-Black trees.

For students learning algorithms, basic BSTs are important because:
1. They introduce tree thinking and recursion
2. They're the foundation for more advanced trees
3. They demonstrate the importance of balance in data structures
4. They show how invariants (BST property) enable efficient algorithms

**Common Student Mistakes:**
- Forgetting to return the modified tree in recursive functions
- Not handling all cases in delete operation
- Confusing BST property (left ≤ root < right vs left < root ≤ right)
- Not considering tree balance in complexity analysis

<!-- ALL -->

## Implementation Exercise

**Problem:** Implement a function to find the $k$-th smallest element in a BST.

**Hint:** Use inorder traversal properties!

```python
def kth_smallest(root, k):
    # Your implementation here
    pass
```

<!-- NOTES-ONLY -->

**Solution and Explanation:**

**Approach 1: Inorder Traversal**
```python
def kth_smallest(root, k):
    def inorder(node, result):
        if node:
            inorder(node.left, result)
            result.append(node.val)
            inorder(node.right, result)
    
    result = []
    inorder(root, result)
    return result[k-1]  # k-th smallest (1-indexed)
```

Time: $O(n)$, Space: $O(n)$

**Approach 2: Optimized Inorder (Early Termination)**
```python
def kth_smallest(root, k):
    def inorder(node):
        if not node:
            return None
        
        # Search left subtree
        left_result = inorder(node.left)
        if left_result is not None:
            return left_result
        
        # Process current node
        self.count += 1
        if self.count == k:
            return node.val
        
        # Search right subtree
        return inorder(node.right)
    
    self.count = 0
    return inorder(root)
```

Time: $O(k)$ in best case, Space: $O(h)$

**Approach 3: Iterative with Stack**
```python
def kth_smallest(root, k):
    stack = []
    current = root
    count = 0
    
    while stack or current:
        # Go to leftmost node
        while current:
            stack.append(current)
            current = current.left
        
        # Process node
        current = stack.pop()
        count += 1
        if count == k:
            return current.val
        
        # Move to right subtree
        current = current.right
    
    return None
```

This approach is space-efficient and stops early.

<!-- ALL -->

## Summary

### Key Takeaways

1. **BST Property:** Left ≤ Root < Right (recursively)
2. **Operations:** All major operations are $O(h)$ where $h$ is height
3. **Balance Matters:** Balanced trees give $O(\\log n)$, skewed trees give $O(n)$
4. **Inorder Traversal:** Gives sorted sequence
5. **Trade-offs:** Good for sorted access, but not constant-time like hash tables

### Next Lecture Preview

- Self-balancing BSTs (AVL Trees)
- Rotation operations
- Maintaining balance automatically
- Guaranteed $O(\\log n)$ performance

### Homework

1. Implement BST with insert, search, delete operations
2. Add inorder, preorder, postorder traversal methods
3. Implement `find_min()`, `find_max()`, and `kth_smallest()`
4. Analyze time complexity of your implementations
5. Test with various input patterns (sorted, random, reverse-sorted)
"""
        
        # Test processing this complex academic content
        result = self.splitter.process_directives(cs_lecture)
        
        # Verify content splitting
        assert "Binary Search Trees" in result["slides"]
        assert "Binary Search Trees" in result["notes"]
        
        # Check that notes-only content is properly separated
        assert "Important Notes for Students" in result["notes"]
        assert "Important Notes for Students" not in result["slides"]
        
        # Check that code examples are in both
        assert "def search(root, key):" in result["slides"]
        assert "def search(root, key):" in result["notes"]
        
        # Check mathematical expressions
        assert "$O(\\log n)$" in result["slides"]
        assert "$O(\\log n)$" in result["notes"]
        
        # Verify LaTeX validation
        latex_result = self.splitter.get_latex_validation_result()
        assert latex_result is not None
        
        # Generate Quarto files
        slides_path, notes_path = self.splitter.generate_quarto_files(
            str(self.temp_path / "cs_lecture.md"),
            str(self.temp_path / "output")
        )
        
        # Verify files were created
        assert Path(slides_path).exists()
        assert Path(notes_path).exists()
        
        # Check YAML frontmatter
        slides_content = Path(slides_path).read_text()
        notes_content = Path(notes_path).read_text()
        
        assert slides_content.startswith("---\n")
        assert notes_content.startswith("---\n")
        assert "Data Structures and Algorithms" in slides_content
        assert "Lecture Notes" in notes_content
    
    def test_mathematics_lecture(self):
        """Test with mathematics lecture content."""
        math_lecture = """---
title: "Real Analysis - Lecture 12"
author: "Prof. Mathematics"
date: "2024-03-10"
---

# Uniform Convergence of Function Sequences

## Motivation

Why do we need uniform convergence when we already have pointwise convergence?

**Example:** Consider $f_n(x) = x^n$ on $[0,1]$

- **Pointwise limit:** $f(x) = \\begin{cases} 0 & \\text{if } 0 \\leq x < 1 \\\\ 1 & \\text{if } x = 1 \\end{cases}$
- Each $f_n$ is continuous, but $f$ is not!
- **Problem:** Continuity is not preserved under pointwise convergence

<!-- SLIDE -->

## Definition: Uniform Convergence

**Definition 1:** A sequence of functions $(f_n)$ converges **uniformly** to $f$ on $D$ if:

$$\\forall \\varepsilon > 0, \\exists N \\in \\mathbb{N} : n \\geq N \\Rightarrow \\sup_{x \\in D} |f_n(x) - f(x)| < \\varepsilon$$

**Equivalent formulation:**
$$\\lim_{n \\to \\infty} \\sup_{x \\in D} |f_n(x) - f(x)| = 0$$

### Notation
We write $f_n \\rightrightarrows f$ on $D$ for uniform convergence.

<!-- NOTES-ONLY -->

**Pedagogical Notes:**

The key insight is that uniform convergence requires the convergence to be "uniform" across the entire domain. In pointwise convergence, for each fixed $x$, we can choose $N$ depending on $x$. In uniform convergence, we need a single $N$ that works for all $x$ simultaneously.

**Visual Interpretation:** 
- Pointwise: For each vertical line $x = a$, $f_n(a) \\to f(a)$
- Uniform: The entire graph of $f_n$ gets arbitrarily close to the graph of $f$

**Common Student Confusion:**
Students often think uniform convergence is just "faster" pointwise convergence. Emphasize that it's a fundamentally different type of convergence that preserves more properties.

<!-- ALL -->

<!-- SLIDE -->

## Uniform vs Pointwise Convergence

### Example 1: $f_n(x) = \\frac{x}{1 + nx^2}$ on $\\mathbb{R}$

**Pointwise limit:** $f(x) = 0$ for all $x \\in \\mathbb{R}$

**Analysis:**
- For fixed $x \\neq 0$: $|f_n(x)| = \\frac{|x|}{1 + n x^2} \\to 0$ as $n \\to \\infty$
- For $x = 0$: $f_n(0) = 0$ for all $n$

**Uniform convergence?**
$$\\sup_{x \\in \\mathbb{R}} |f_n(x)| = \\sup_{x \\in \\mathbb{R}} \\frac{|x|}{1 + nx^2}$$

To find maximum, differentiate: $\\frac{d}{dx}\\left(\\frac{x}{1 + nx^2}\\right) = \\frac{1 - nx^2}{(1 + nx^2)^2}$

Critical point: $x = \\pm\\frac{1}{\\sqrt{n}}$

Maximum value: $f_n\\left(\\frac{1}{\\sqrt{n}}\\right) = \\frac{1/\\sqrt{n}}{1 + n \\cdot 1/n} = \\frac{1}{2\\sqrt{n}} \\to 0$

**Conclusion:** $f_n \\rightrightarrows 0$ on $\\mathbb{R}$

<!-- NOTES-ONLY -->

**Detailed Calculation for Students:**

Let's work through the optimization carefully:

$$g(x) = \\frac{x}{1 + nx^2} \\text{ for } x \\geq 0$$

$$g'(x) = \\frac{(1 + nx^2) \\cdot 1 - x \\cdot 2nx}{(1 + nx^2)^2} = \\frac{1 + nx^2 - 2nx^2}{(1 + nx^2)^2} = \\frac{1 - nx^2}{(1 + nx^2)^2}$$

Setting $g'(x) = 0$: $1 - nx^2 = 0 \\Rightarrow x^2 = \\frac{1}{n} \\Rightarrow x = \\frac{1}{\\sqrt{n}}$

At this point:
$$g\\left(\\frac{1}{\\sqrt{n}}\\right) = \\frac{1/\\sqrt{n}}{1 + n \\cdot (1/n)} = \\frac{1/\\sqrt{n}}{1 + 1} = \\frac{1}{2\\sqrt{n}}$$

Since $g'(x) > 0$ for $x < 1/\\sqrt{n}$ and $g'(x) < 0$ for $x > 1/\\sqrt{n}$, this is indeed a maximum.

By symmetry, the global maximum of $|f_n(x)|$ is $\\frac{1}{2\\sqrt{n}}$.

Therefore: $\\sup_{x \\in \\mathbb{R}} |f_n(x) - 0| = \\frac{1}{2\\sqrt{n}} \\to 0$ as $n \\to \\infty$.

<!-- ALL -->

<!-- SLIDE -->

### Example 2: $g_n(x) = nx(1-x)^n$ on $[0,1]$

**Pointwise limit:** $g(x) = 0$ for all $x \\in [0,1]$

**Uniform convergence analysis:**
Need to find $\\sup_{x \\in [0,1]} |g_n(x)|$

Differentiate: $g_n'(x) = n(1-x)^n - n^2 x(1-x)^{n-1} = n(1-x)^{n-1}[1-x-nx] = n(1-x)^{n-1}[1-(n+1)x]$

Critical point: $x = \\frac{1}{n+1}$

Maximum: $g_n\\left(\\frac{1}{n+1}\\right) = n \\cdot \\frac{1}{n+1} \\cdot \\left(1-\\frac{1}{n+1}\\right)^n = \\frac{n}{n+1} \\cdot \\left(\\frac{n}{n+1}\\right)^n$

As $n \\to \\infty$: $\\left(\\frac{n}{n+1}\\right)^n = \\left(\\frac{1}{1+1/n}\\right)^n \\to \\frac{1}{e}$

So: $\\sup_{x \\in [0,1]} |g_n(x)| \\to \\frac{1}{e} \\neq 0$

**Conclusion:** $g_n$ does NOT converge uniformly to $0$

<!-- SLIDE -->

## Theorems: Properties Preserved by Uniform Convergence

### Theorem 1: Continuity
If $f_n \\rightrightarrows f$ on $D$ and each $f_n$ is continuous on $D$, then $f$ is continuous on $D$.

### Theorem 2: Integration
If $f_n \\rightrightarrows f$ on $[a,b]$ and each $f_n$ is Riemann integrable, then:
$$\\lim_{n \\to \\infty} \\int_a^b f_n(x) dx = \\int_a^b f(x) dx$$

### Theorem 3: Differentiation (with conditions)
If $f_n \\to f$ pointwise, $f_n' \\rightrightarrows g$, and each $f_n'$ is continuous, then:
$$f'(x) = g(x) \\text{ and } f_n' \\rightrightarrows f'$$

<!-- NOTES-ONLY -->

**Proof Sketch for Theorem 1 (Continuity):**

Let $\\varepsilon > 0$ and $x_0 \\in D$. We want to show $f$ is continuous at $x_0$.

Since $f_n \\rightrightarrows f$, choose $N$ such that $\\sup_{x \\in D} |f_n(x) - f(x)| < \\varepsilon/3$ for $n \\geq N$.

Since $f_N$ is continuous at $x_0$, choose $\\delta > 0$ such that $|x - x_0| < \\delta \\Rightarrow |f_N(x) - f_N(x_0)| < \\varepsilon/3$.

For $|x - x_0| < \\delta$:
$$|f(x) - f(x_0)| \\leq |f(x) - f_N(x)| + |f_N(x) - f_N(x_0)| + |f_N(x_0) - f(x_0)|$$
$$< \\frac{\\varepsilon}{3} + \\frac{\\varepsilon}{3} + \\frac{\\varepsilon}{3} = \\varepsilon$$

Therefore $f$ is continuous at $x_0$.

**Important Note on Theorem 3:**
The differentiation theorem requires uniform convergence of the derivatives, not the functions themselves. This is a common source of confusion. The classic counterexample is $f_n(x) = \\frac{\\sin(nx)}{\\sqrt{n}}$ which converges uniformly to $0$, but $f_n'(x) = \\sqrt{n}\\cos(nx)$ does not converge at all.

<!-- ALL -->

## The Weierstrass M-Test

**Theorem (Weierstrass M-Test):** Let $(f_n)$ be a sequence of functions on $D$. If there exists a sequence $(M_n)$ of positive numbers such that:

1. $|f_n(x)| \\leq M_n$ for all $x \\in D$ and all $n$
2. $\\sum_{n=1}^\\infty M_n$ converges

Then $\\sum_{n=1}^\\infty f_n(x)$ converges uniformly on $D$.

### Example Application

Consider $\\sum_{n=1}^\\infty \\frac{\\sin(nx)}{n^2}$ on $\\mathbb{R}$.

- $\\left|\\frac{\\sin(nx)}{n^2}\\right| \\leq \\frac{1}{n^2}$ for all $x$
- $\\sum_{n=1}^\\infty \\frac{1}{n^2} = \\frac{\\pi^2}{6}$ converges

By M-test: $\\sum_{n=1}^\\infty \\frac{\\sin(nx)}{n^2}$ converges uniformly on $\\mathbb{R}$

<!-- SLIDE -->

## Summary and Applications

### Key Concepts
1. **Uniform convergence** is stronger than pointwise convergence
2. **Preserves continuity** (pointwise convergence doesn't)
3. **Allows interchange** of limit and integral
4. **M-test** provides practical criterion for uniform convergence

### Applications
- **Fourier series:** Uniform convergence ensures continuity of sum
- **Power series:** Uniform convergence on compact subsets
- **Approximation theory:** Weierstrass approximation theorem
- **Differential equations:** Existence and uniqueness theorems

### Next Lecture
- **Equicontinuity** and the **Arzelà-Ascoli theorem**
- **Stone-Weierstrass theorem**
- Applications to **approximation theory**
"""
        
        # Test processing mathematics content
        result = self.splitter.process_directives(math_lecture)
        
        # Verify mathematical content is preserved
        assert "\\sup_{x \\in D}" in result["slides"]
        assert "\\sup_{x \\in D}" in result["notes"]
        assert "\\rightrightarrows" in result["slides"]
        
        # Check complex mathematical expressions
        assert "\\lim_{n \\to \\infty}" in result["notes"]
        assert "\\sum_{n=1}^\\infty" in result["slides"]
        
        # Verify notes-only pedagogical content
        assert "Pedagogical Notes" in result["notes"]
        assert "Pedagogical Notes" not in result["slides"]
        assert "Common Student Confusion" in result["notes"]
        
        # Check LaTeX validation
        latex_result = self.splitter.get_latex_validation_result()
        assert latex_result is not None
        # Should detect advanced math packages needed
        assert len(latex_result.packages_required) > 0
    
    def test_physics_lecture_with_equations(self):
        """Test with physics lecture containing complex equations."""
        physics_lecture = """---
title: "Quantum Mechanics - Lecture 15"
author: "Prof. Physics"
date: "2024-04-05"
---

# The Schrödinger Equation

## Time-Dependent Schrödinger Equation

The fundamental equation of quantum mechanics:

$$i\\hbar \\frac{\\partial \\Psi(\\mathbf{r},t)}{\\partial t} = \\hat{H} \\Psi(\\mathbf{r},t)$$

Where:
- $\\Psi(\\mathbf{r},t)$ is the wave function
- $\\hat{H}$ is the Hamiltonian operator
- $\\hbar = \\frac{h}{2\\pi}$ is the reduced Planck constant

<!-- SLIDE -->

## Hamiltonian for a Particle in a Potential

$$\\hat{H} = \\hat{T} + \\hat{V} = -\\frac{\\hbar^2}{2m}\\nabla^2 + V(\\mathbf{r})$$

In one dimension:
$$\\hat{H} = -\\frac{\\hbar^2}{2m}\\frac{\\partial^2}{\\partial x^2} + V(x)$$

### Complete Time-Dependent Equation

$$i\\hbar \\frac{\\partial \\Psi(x,t)}{\\partial t} = -\\frac{\\hbar^2}{2m}\\frac{\\partial^2 \\Psi(x,t)}{\\partial x^2} + V(x)\\Psi(x,t)$$

<!-- NOTES-ONLY -->

**Historical Context:**

Erwin Schrödinger developed this equation in 1925, building on de Broglie's matter wave hypothesis and the correspondence principle. The equation was initially met with skepticism because it seemed to describe particles as waves, contradicting classical intuition.

**Mathematical Structure:**
- Linear partial differential equation
- First order in time, second order in space
- Complex-valued solutions (wave function)
- Deterministic evolution (given initial conditions)

**Physical Interpretation:**
The wave function $\\Psi(x,t)$ contains all information about the quantum system. Its absolute square $|\\Psi(x,t)|^2$ gives the probability density of finding the particle at position $x$ at time $t$.

<!-- ALL -->

<!-- SLIDE -->

## Separation of Variables

For time-independent potentials $V(x)$, assume:
$$\\Psi(x,t) = \\psi(x) \\phi(t)$$

Substituting into the Schrödinger equation:
$$i\\hbar \\psi(x) \\frac{d\\phi(t)}{dt} = \\phi(t) \\left[-\\frac{\\hbar^2}{2m}\\frac{d^2\\psi(x)}{dx^2} + V(x)\\psi(x)\\right]$$

Dividing by $\\psi(x)\\phi(t)$:
$$i\\hbar \\frac{1}{\\phi(t)}\\frac{d\\phi(t)}{dt} = \\frac{1}{\\psi(x)}\\left[-\\frac{\\hbar^2}{2m}\\frac{d^2\\psi(x)}{dx^2} + V(x)\\psi(x)\\right]$$

Since left side depends only on $t$ and right side only on $x$, both equal a constant $E$:

$$i\\hbar \\frac{d\\phi(t)}{dt} = E\\phi(t) \\quad \\Rightarrow \\quad \\phi(t) = e^{-iEt/\\hbar}$$

$$-\\frac{\\hbar^2}{2m}\\frac{d^2\\psi(x)}{dx^2} + V(x)\\psi(x) = E\\psi(x)$$

<!-- SLIDE -->

## Time-Independent Schrödinger Equation

$$\\hat{H}\\psi(x) = E\\psi(x)$$

This is an **eigenvalue equation**:
- $\\psi(x)$ are the **eigenfunctions** (energy eigenstates)
- $E$ are the **eigenvalues** (energy levels)

### General Solution

$$\\Psi(x,t) = \\sum_n c_n \\psi_n(x) e^{-iE_n t/\\hbar}$$

Where $c_n$ are determined by initial conditions:
$$c_n = \\langle \\psi_n | \\Psi(x,0) \\rangle = \\int_{-\\infty}^{\\infty} \\psi_n^*(x) \\Psi(x,0) dx$$

<!-- NOTES-ONLY -->

**Eigenvalue Problem Details:**

The time-independent Schrödinger equation is a Sturm-Liouville problem. For physically acceptable solutions, we need:

1. **Normalizability:** $\\int_{-\\infty}^{\\infty} |\\psi(x)|^2 dx < \\infty$
2. **Continuity:** $\\psi(x)$ must be continuous
3. **Continuity of derivative:** $\\psi'(x)$ continuous except at infinite potential jumps

These boundary conditions lead to quantization of energy levels in bound states.

**Superposition Principle:**
The general solution is a linear combination of energy eigenstates. The coefficients $c_n$ determine the probability amplitude of measuring energy $E_n$:

$$P(E_n) = |c_n|^2$$

**Time Evolution:**
Each energy eigenstate evolves with its own phase factor $e^{-iE_n t/\\hbar}$. The relative phases between different energy components change with time, leading to quantum interference effects.

<!-- ALL -->

## Example: Infinite Square Well

Potential: $V(x) = \\begin{cases} 0 & \\text{if } 0 < x < L \\\\ \\infty & \\text{otherwise} \\end{cases}$

Inside the well ($0 < x < L$):
$$-\\frac{\\hbar^2}{2m}\\frac{d^2\\psi}{dx^2} = E\\psi$$

General solution: $\\psi(x) = A\\sin(kx) + B\\cos(kx)$ where $k = \\sqrt{\\frac{2mE}{\\hbar^2}}$

**Boundary conditions:** $\\psi(0) = \\psi(L) = 0$

From $\\psi(0) = 0$: $B = 0$
From $\\psi(L) = 0$: $A\\sin(kL) = 0$

For non-trivial solutions: $kL = n\\pi$ where $n = 1, 2, 3, ...$

<!-- SLIDE -->

### Infinite Square Well Solutions

**Energy levels:**
$$E_n = \\frac{n^2 \\pi^2 \\hbar^2}{2mL^2} \\quad n = 1, 2, 3, ...$$

**Normalized wave functions:**
$$\\psi_n(x) = \\sqrt{\\frac{2}{L}} \\sin\\left(\\frac{n\\pi x}{L}\\right)$$

**Complete time-dependent solution:**
$$\\Psi_n(x,t) = \\sqrt{\\frac{2}{L}} \\sin\\left(\\frac{n\\pi x}{L}\\right) e^{-iE_n t/\\hbar}$$

### Key Features
- **Quantized energy:** $E_n \\propto n^2$
- **Zero-point energy:** $E_1 = \\frac{\\pi^2 \\hbar^2}{2mL^2} \\neq 0$
- **Orthogonal states:** $\\langle \\psi_m | \\psi_n \\rangle = \\delta_{mn}$

<!-- NOTES-ONLY -->

**Physical Insights:**

1. **Quantization Origin:** Boundary conditions force standing wave patterns, leading to discrete allowed wavelengths and hence discrete energies.

2. **Zero-Point Energy:** Even the ground state ($n=1$) has non-zero energy. This is a purely quantum effect - classically, a particle could have zero kinetic energy.

3. **Energy Scaling:** 
   - $E_n \\propto 1/L^2$: Smaller box → higher energies (uncertainty principle)
   - $E_n \\propto 1/m$: Lighter particles → higher energies
   - $E_n \\propto n^2$: Energy gaps increase with quantum number

4. **Classical Limit:** As $n \\to \\infty$, the probability distribution approaches the classical uniform distribution (correspondence principle).

**Normalization Check:**
$$\\int_0^L |\\psi_n(x)|^2 dx = \\frac{2}{L} \\int_0^L \\sin^2\\left(\\frac{n\\pi x}{L}\\right) dx = \\frac{2}{L} \\cdot \\frac{L}{2} = 1 \\checkmark$$

**Orthogonality Check:**
$$\\int_0^L \\psi_m^*(x) \\psi_n(x) dx = \\frac{2}{L} \\int_0^L \\sin\\left(\\frac{m\\pi x}{L}\\right) \\sin\\left(\\frac{n\\pi x}{L}\\right) dx = \\delta_{mn}$$

<!-- ALL -->

## Probability and Expectation Values

For a normalized wave function $\\Psi(x,t)$:

**Probability density:** $\\rho(x,t) = |\\Psi(x,t)|^2$

**Probability of finding particle in $[a,b]$:**
$$P(a \\leq x \\leq b) = \\int_a^b |\\Psi(x,t)|^2 dx$$

**Expectation value of observable $\\hat{A}$:**
$$\\langle \\hat{A} \\rangle = \\langle \\Psi | \\hat{A} | \\Psi \\rangle = \\int_{-\\infty}^{\\infty} \\Psi^*(x,t) \\hat{A} \\Psi(x,t) dx$$

### Important Expectation Values

**Position:** $\\langle x \\rangle = \\int_{-\\infty}^{\\infty} \\Psi^*(x,t) \\, x \\, \\Psi(x,t) dx$

**Momentum:** $\\langle p \\rangle = \\int_{-\\infty}^{\\infty} \\Psi^*(x,t) \\left(-i\\hbar \\frac{\\partial}{\\partial x}\\right) \\Psi(x,t) dx$

**Energy:** $\\langle E \\rangle = \\int_{-\\infty}^{\\infty} \\Psi^*(x,t) \\hat{H} \\Psi(x,t) dx$

## Summary

1. **Schrödinger equation** governs quantum evolution
2. **Separation of variables** leads to energy eigenstates
3. **Boundary conditions** cause energy quantization
4. **Wave function** contains complete quantum information
5. **Expectation values** connect quantum formalism to measurements
"""
        
        # Test processing physics content
        result = self.splitter.process_directives(physics_lecture)
        
        # Verify complex physics equations are preserved
        assert "\\frac{\\partial \\Psi}{\\partial t}" in result["slides"]
        assert "\\hat{H}" in result["slides"]
        assert "\\nabla^2" in result["slides"]
        
        # Check that detailed derivations are in notes
        assert "Historical Context" in result["notes"]
        assert "Historical Context" not in result["slides"]
        
        # Verify mathematical structures
        assert "\\begin{cases}" in result["slides"]
        assert "\\sum_n c_n" in result["slides"]
        
        # Check LaTeX validation for physics packages
        latex_result = self.splitter.get_latex_validation_result()
        assert latex_result is not None


class TestAcademicContentPatterns:
    """Test common patterns found in academic content."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.splitter = ContentSplitter()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_multilingual_content(self):
        """Test content with multiple languages."""
        multilingual_content = """---
title: "Linguistique Computationnelle"
author: "Prof. Linguistique"
---

# Traitement Automatique des Langues

## Introduction

Le **traitement automatique des langues** (TAL) est une discipline qui combine:
- Linguistique théorique
- Informatique
- Intelligence artificielle

<!-- SLIDE -->

## Analyse Morphologique

### Exemple en français

**Mot:** "mangions"
- **Lemme:** manger
- **Catégorie:** verbe
- **Traits:** 1ère personne, pluriel, imparfait

### Mathematical Model

Probability of morphological analysis:
$$P(\\text{analysis}|\\text{word}) = \\frac{P(\\text{word}|\\text{analysis}) \\cdot P(\\text{analysis})}{P(\\text{word})}$$

<!-- NOTES-ONLY -->

**Notes pédagogiques:**

Les étudiants ont souvent des difficultés avec la notion de lemmatisation. Il est important de distinguer:

1. **Lemmatisation:** Réduction à la forme canonique (dictionnaire)
2. **Racinisation (stemming):** Suppression des affixes (approximative)

**Exemple comparatif:**
- Mot: "couraient"
- Lemmatisation: "courir"
- Racinisation: "cour"

La lemmatisation nécessite une analyse morphologique complète, tandis que la racinisation utilise des règles heuristiques.

<!-- ALL -->

## Análisis Sintáctico (Español)

### Gramática de Constituyentes

**Reglas de producción:**
- S → SN SV
- SN → Det N
- SV → V SN

**Ejemplo:** "El gato come pescado"

```
       S
      / \\
     SN  SV
    / |  | \\
  Det N  V  SN
   |  |  |   |
  El gato come pescado
```

<!-- SLIDE -->

## Syntactic Analysis (English)

### Dependency Grammar

**Relations:**
- nsubj(eat, cat) - nominal subject
- det(cat, the) - determiner
- dobj(eat, fish) - direct object

**Universal Dependencies example:**

```
The cat eats fish
det nsubj root dobj
 ↘   ↓    ↑    ↙
   cat ← eats → fish
     ↑
    The
```

### Parsing Algorithms

**CKY Algorithm complexity:** $O(n^3 |G|)$
- $n$: sentence length
- $|G|$: grammar size

<!-- NOTES-ONLY -->

**Cross-linguistic Considerations:**

Different languages pose different challenges for computational analysis:

**French:**
- Rich morphology (verb conjugations, agreement)
- Relatively fixed word order (SVO)
- Liaison phenomena in phonology

**Spanish:**
- Pro-drop language (null subjects)
- Flexible word order for emphasis
- Complex clitic system

**English:**
- Minimal inflectional morphology
- Fixed word order (crucial for meaning)
- Extensive use of phrasal verbs

**Universal Dependencies:**
The UD framework attempts to provide consistent annotation across languages, but language-specific phenomena still require special treatment.

<!-- ALL -->

## 中文信息处理 (Chinese NLP)

### 词汇分割 (Word Segmentation)

**问题:** 中文没有明显的词边界

**例子:** "我爱自然语言处理"

**可能的分割:**
1. 我 / 爱 / 自然 / 语言 / 处理
2. 我 / 爱 / 自然语言 / 处理  
3. 我 / 爱 / 自然语言处理

### Mathematical Approach

**Maximum Matching Algorithm:**
$$\\text{segmentation} = \\arg\\max_{s} \\prod_{w \\in s} P(w)$$

Where $P(w)$ is the probability of word $w$ in the language.

## Summary - Résumé - Resumen - 总结

**Key Challenges in Multilingual NLP:**
1. **Morphological complexity** varies across languages
2. **Word order** differences affect parsing strategies  
3. **Writing systems** create different tokenization needs
4. **Cultural context** influences semantic interpretation

**Défis principaux:**
- Adaptation des algorithmes aux spécificités linguistiques
- Gestion de la variation dialectale
- Traitement des langues peu dotées en ressources

**Desafíos principales:**
- Análisis de lenguas con morfología rica
- Procesamiento de orden de palabras flexible
- Manejo de fenómenos específicos del español

**主要挑战:**
- 词汇分割的准确性
- 语法分析的复杂性
- 语义理解的文化背景
"""
        
        # Test multilingual content processing
        result = self.splitter.process_directives(multilingual_content)
        
        # Verify all languages are preserved
        assert "Traitement Automatique" in result["slides"]
        assert "Análisis Sintáctico" in result["slides"]
        assert "Syntactic Analysis" in result["slides"]
        assert "中文信息处理" in result["slides"]
        
        # Check mathematical content in multilingual context
        assert "P(\\text{analysis}|\\text{word})" in result["slides"]
        assert "O(n^3 |G|)" in result["slides"]
        
        # Verify notes-only content in different languages
        assert "Notes pédagogiques" in result["notes"]
        assert "Cross-linguistic Considerations" in result["notes"]
        assert "Notes pédagogiques" not in result["slides"]
    
    def test_code_heavy_content(self):
        """Test content with extensive code examples."""
        code_heavy_content = """---
title: "Advanced Python Programming"
author: "Prof. Computer Science"
---

# Object-Oriented Design Patterns

## The Strategy Pattern

**Problem:** Need to define a family of algorithms, encapsulate each one, and make them interchangeable.

<!-- SLIDE -->

### Implementation

```python
from abc import ABC, abstractmethod
from typing import List

class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: List[int]) -> List[int]:
        pass

class BubbleSort(SortStrategy):
    def sort(self, data: List[int]) -> List[int]:
        arr = data.copy()
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr

class QuickSort(SortStrategy):
    def sort(self, data: List[int]) -> List[int]:
        if len(data) <= 1:
            return data
        
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        
        return (self.sort(left) + middle + self.sort(right))

class SortContext:
    def __init__(self, strategy: SortStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: SortStrategy):
        self._strategy = strategy
    
    def sort_data(self, data: List[int]) -> List[int]:
        return self._strategy.sort(data)
```

<!-- NOTES-ONLY -->

**Implementation Details and Best Practices:**

**Type Hints:** Notice the extensive use of type hints (`List[int]`, `SortStrategy`). This improves code readability and enables better IDE support and static analysis.

**Abstract Base Classes:** The `ABC` and `@abstractmethod` ensure that concrete strategies must implement the `sort` method. This enforces the contract at the class level.

**Defensive Copying:** In `BubbleSort.sort()`, we use `data.copy()` to avoid modifying the original list. This is crucial for maintaining immutability and preventing side effects.

**List Comprehensions:** The `QuickSort` implementation uses list comprehensions for partitioning, which is more Pythonic than traditional loops.

**Strategy Pattern Benefits:**
1. **Open/Closed Principle:** Open for extension (new strategies), closed for modification
2. **Single Responsibility:** Each strategy has one reason to change
3. **Composition over Inheritance:** Context uses strategy rather than inheriting from it

**Common Mistakes:**
- Forgetting to copy data in sorting algorithms
- Not handling edge cases (empty lists, single elements)
- Mixing strategy selection logic with strategy implementation

<!-- ALL -->

<!-- SLIDE -->

### Usage Example

```python
# Client code
def main():
    data = [64, 34, 25, 12, 22, 11, 90]
    
    # Use bubble sort
    context = SortContext(BubbleSort())
    result1 = context.sort_data(data)
    print(f"Bubble sort: {result1}")
    
    # Switch to quick sort
    context.set_strategy(QuickSort())
    result2 = context.sort_data(data)
    print(f"Quick sort: {result2}")
    
    # Performance comparison
    import time
    import random
    
    large_data = [random.randint(1, 1000) for _ in range(1000)]
    
    strategies = [
        ("Bubble Sort", BubbleSort()),
        ("Quick Sort", QuickSort())
    ]
    
    for name, strategy in strategies:
        context.set_strategy(strategy)
        start_time = time.time()
        context.sort_data(large_data)
        end_time = time.time()
        print(f"{name}: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    main()
```

**Expected Output:**
```
Bubble sort: [11, 12, 22, 25, 34, 64, 90]
Quick sort: [11, 12, 22, 25, 34, 64, 90]
Bubble Sort: 0.1234 seconds
Quick Sort: 0.0056 seconds
```

<!-- SLIDE -->

## The Observer Pattern

**Problem:** Define a one-to-many dependency between objects so that when one object changes state, all dependents are notified.

### Implementation

```python
from typing import List, Protocol

class Observer(Protocol):
    def update(self, subject: 'Subject') -> None:
        ...

class Subject:
    def __init__(self):
        self._observers: List[Observer] = []
        self._state: int = 0
    
    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self)
    
    @property
    def state(self) -> int:
        return self._state
    
    @state.setter
    def state(self, value: int) -> None:
        self._state = value
        self.notify()

class ConcreteObserver:
    def __init__(self, name: str):
        self.name = name
    
    def update(self, subject: Subject) -> None:
        print(f"{self.name} received update: state = {subject.state}")

# Usage
subject = Subject()
observer1 = ConcreteObserver("Observer 1")
observer2 = ConcreteObserver("Observer 2")

subject.attach(observer1)
subject.attach(observer2)

subject.state = 42  # Triggers notification
subject.state = 100  # Triggers notification
```

<!-- NOTES-ONLY -->

**Advanced Observer Pattern Considerations:**

**Protocol vs ABC:** This implementation uses `Protocol` (structural typing) instead of `ABC` (nominal typing). This is more flexible as any class with an `update` method can be an observer without explicit inheritance.

**Memory Management:** Be careful with observer references. If observers hold references to the subject and vice versa, you can create circular references. Consider using weak references:

```python
import weakref

class Subject:
    def __init__(self):
        self._observers: List[weakref.ReferenceType] = []
    
    def attach(self, observer: Observer) -> None:
        self._observers.append(weakref.ref(observer))
    
    def notify(self) -> None:
        # Clean up dead references
        self._observers = [ref for ref in self._observers if ref() is not None]
        for ref in self._observers:
            observer = ref()
            if observer:
                observer.update(self)
```

**Thread Safety:** In multi-threaded environments, you need to protect the observer list:

```python
import threading

class ThreadSafeSubject(Subject):
    def __init__(self):
        super().__init__()
        self._lock = threading.Lock()
    
    def attach(self, observer: Observer) -> None:
        with self._lock:
            super().attach(observer)
    
    def detach(self, observer: Observer) -> None:
        with self._lock:
            super().detach(observer)
    
    def notify(self) -> None:
        with self._lock:
            observers_copy = self._observers.copy()
        
        for observer in observers_copy:
            observer.update(self)
```

**Event-Driven Architecture:** The Observer pattern is fundamental to event-driven programming, GUI frameworks, and reactive programming paradigms.

<!-- ALL -->

## Decorator Pattern with Python Decorators

**Problem:** Attach additional responsibilities to an object dynamically.

### Function Decorators

```python
import functools
import time
from typing import Callable, Any

def timing_decorator(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

def retry_decorator(max_attempts: int = 3):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(0.1 * (attempt + 1))  # Exponential backoff
            return None
        return wrapper
    return decorator

# Usage
@timing_decorator
@retry_decorator(max_attempts=3)
def unreliable_function(x: int) -> int:
    import random
    if random.random() < 0.7:  # 70% chance of failure
        raise ValueError("Random failure")
    return x * x

# Test
try:
    result = unreliable_function(5)
    print(f"Result: {result}")
except ValueError as e:
    print(f"Function failed: {e}")
```

### Class-Based Decorators

```python
class CacheDecorator:
    def __init__(self, func: Callable):
        self.func = func
        self.cache = {}
        functools.update_wrapper(self, func)
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        # Create cache key from arguments
        key = str(args) + str(sorted(kwargs.items()))
        
        if key in self.cache:
            print(f"Cache hit for {self.func.__name__}")
            return self.cache[key]
        
        print(f"Cache miss for {self.func.__name__}")
        result = self.func(*args, **kwargs)
        self.cache[key] = result
        return result
    
    def clear_cache(self) -> None:
        self.cache.clear()

@CacheDecorator
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Usage
print(fibonacci(10))  # Calculates and caches
print(fibonacci(10))  # Uses cache
```

## Summary

**Design Patterns Covered:**
1. **Strategy Pattern:** Encapsulate algorithms and make them interchangeable
2. **Observer Pattern:** Define one-to-many dependencies between objects
3. **Decorator Pattern:** Add responsibilities to objects dynamically

**Python-Specific Features:**
- Type hints for better code documentation
- Protocols for structural typing
- Function decorators for cross-cutting concerns
- Context managers and properties

**Best Practices:**
- Use composition over inheritance
- Follow SOLID principles
- Leverage Python's dynamic features appropriately
- Consider thread safety in concurrent applications
"""
        
        # Test code-heavy content processing
        result = self.splitter.process_directives(code_heavy_content)
        
        # Verify code blocks are preserved
        assert "class SortStrategy(ABC):" in result["slides"]
        assert "def sort(self, data: List[int])" in result["slides"]
        assert "@abstractmethod" in result["slides"]
        
        # Check that implementation details are in notes
        assert "Implementation Details and Best Practices" in result["notes"]
        assert "Common Mistakes" in result["notes"]
        assert "Thread Safety" in result["notes"]
        
        # Verify complex code structures
        assert "functools.wraps(func)" in result["slides"]
        assert "weakref.ref(observer)" in result["notes"]
        
        # Check that both slides and notes have code
        assert "def fibonacci(n: int)" in result["slides"]
        assert "def fibonacci(n: int)" in result["notes"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])