"""
Comprehensive performance tests for markdown slides generator.

Tests processing speed, memory usage, scalability, and performance
characteristics under various load conditions.
"""

import pytest
import tempfile
import shutil
import time
import psutil
import os
from pathlib import Path
from unittest.mock import Mock, patch
import threading
from concurrent.futures import ThreadPoolExecutor

from markdown_slides_generator.core.content_splitter import ContentSplitter
from markdown_slides_generator.core.quarto_orchestrator import QuartoOrchestrator
from markdown_slides_generator.batch.batch_processor import BatchProcessor
from markdown_slides_generator.config import Config


class TestContentSplitterPerformance:
    """Test performance characteristics of content splitter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.splitter = ContentSplitter()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_large_file_processing_speed(self):
        """Test processing speed for large markdown files."""
        # Create a large markdown file (approximately 1MB)
        sections = []
        for i in range(1000):
            sections.append(f"""
## Section {i}

This is section {i} with substantial content. Lorem ipsum dolor sit amet, 
consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore 
et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation 
ullamco laboris nisi ut aliquip ex ea commodo consequat.

<!-- SLIDE -->

### Mathematical Content {i}

Here's some mathematical content: $f(x) = x^2 + {i}x + {i*2}$

Display math:
$$\\sum_{{j=1}}^{{{i}}} \\frac{{1}}{{j^2}} = \\frac{{\\pi^2}}{{6}}$$

<!-- NOTES-ONLY -->

#### Detailed Explanation {i}

This section provides detailed explanation that only appears in notes.
It includes comprehensive background information, derivations, and 
additional context that students can reference when studying.

The mathematical concepts presented here build upon previous sections
and prepare students for more advanced topics in subsequent lectures.

<!-- ALL -->

#### Summary {i}

Key takeaways from section {i}:
1. Important concept A
2. Important concept B  
3. Important concept C

""")
        
        large_content = '\n'.join(sections)
        file_size = len(large_content.encode('utf-8'))
        
        print(f"Testing with file size: {file_size / 1024 / 1024:.2f} MB")
        
        # Measure processing time
        start_time = time.time()
        result = self.splitter.process_directives(large_content)
        processing_time = time.time() - start_time
        
        print(f"Processing time: {processing_time:.3f} seconds")
        print(f"Processing speed: {file_size / 1024 / 1024 / processing_time:.2f} MB/s")
        
        # Performance assertions
        assert processing_time < 10.0  # Should process 1MB in under 10 seconds
        assert len(result["slides"]) > 0
        assert len(result["notes"]) > 0
        assert len(result["blocks"]) > 0
        
        # Check that content was properly split
        slides_size = len(result["slides"])
        notes_size = len(result["notes"])
        
        print(f"Slides content: {slides_size / 1024:.1f} KB")
        print(f"Notes content: {notes_size / 1024:.1f} KB")
        
        # Notes should be larger (contains notes-only content)
        assert notes_size > slides_size
    
    def test_many_directives_performance(self):
        """Test performance with many directive transitions."""
        # Create content with frequent directive changes
        content_parts = ["# Performance Test Document\n\n"]
        
        for i in range(2000):  # 2000 directive pairs = 6000 total directives
            content_parts.extend([
                f"Content block {i}. ",
                "<!-- SLIDE-ONLY -->",
                f"Slide-specific content {i}. ",
                "<!-- NOTES-ONLY -->", 
                f"Notes-specific content {i}. ",
                "<!-- ALL -->"
            ])
        
        content = ''.join(content_parts)
        directive_count = content.count('<!--')
        
        print(f"Testing with {directive_count} directives")
        
        start_time = time.time()
        result = self.splitter.process_directives(content)
        processing_time = time.time() - start_time
        
        print(f"Directive processing time: {processing_time:.3f} seconds")
        print(f"Directives per second: {directive_count / processing_time:.0f}")
        
        # Performance assertions
        assert processing_time < 5.0  # Should handle 6000 directives in under 5 seconds
        assert len(result["directives"]) == directive_count
        assert directive_count / processing_time > 1000  # At least 1000 directives/second
    
    def test_memory_usage_large_files(self):
        """Test memory usage characteristics with large files."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create progressively larger files and measure memory
        memory_measurements = []
        
        for size_factor in [1, 2, 4, 8]:
            # Create content
            content_size = 100 * size_factor  # 100, 200, 400, 800 sections
            sections = []
            
            for i in range(content_size):
                sections.append(f"""
## Section {i}
Content with math: $x_{i} = \\sum_{{j=1}}^{i} j^2$
<!-- SLIDE -->
Slide content {i}
<!-- NOTES-ONLY -->
Notes content {i} with detailed explanation.
<!-- ALL -->
""")
            
            content = '\n'.join(sections)
            
            # Process and measure memory
            before_memory = process.memory_info().rss / 1024 / 1024
            result = self.splitter.process_directives(content)
            after_memory = process.memory_info().rss / 1024 / 1024
            
            memory_used = after_memory - before_memory
            content_mb = len(content.encode('utf-8')) / 1024 / 1024
            
            memory_measurements.append({
                'content_size_mb': content_mb,
                'memory_used_mb': memory_used,
                'memory_ratio': memory_used / content_mb if content_mb > 0 else 0
            })
            
            print(f"Content: {content_mb:.1f} MB, Memory used: {memory_used:.1f} MB, "
                  f"Ratio: {memory_used / content_mb:.1f}x")
        
        # Memory usage should be reasonable (not more than 10x content size)
        for measurement in memory_measurements:
            assert measurement['memory_ratio'] < 10.0
    
    def test_concurrent_processing_safety(self):
        """Test thread safety of content splitter."""
        # Create multiple content pieces
        contents = []
        for i in range(10):
            content = f"""
# Document {i}
<!-- SLIDE-ONLY -->
Slide content {i}
<!-- NOTES-ONLY -->
Notes content {i}
<!-- ALL -->
Shared content {i}
"""
            contents.append(content)
        
        results = []
        errors = []
        
        def process_content(content):
            try:
                splitter = ContentSplitter()  # Each thread gets its own instance
                result = splitter.process_directives(content)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Process concurrently
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_content, content) for content in contents]
            for future in futures:
                future.result()  # Wait for completion
        
        processing_time = time.time() - start_time
        
        print(f"Concurrent processing time: {processing_time:.3f} seconds")
        
        # All should succeed
        assert len(errors) == 0
        assert len(results) == 10
        
        # Results should be consistent
        for result in results:
            assert "slides" in result
            assert "notes" in result
            assert len(result["blocks"]) > 0


class TestBatchProcessingPerformance:
    """Test performance characteristics of batch processing."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.config.batch.parallel = True
        self.config.batch.max_workers = 4
        self.config.output.formats = ['html']
        
        self.processor = BatchProcessor(self.config)
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_scalability_with_file_count(self):
        """Test scalability with increasing number of files."""
        file_counts = [10, 25, 50, 100]
        processing_times = []
        
        for file_count in file_counts:
            # Create test files
            test_dir = self.temp_path / f"test_{file_count}"
            test_dir.mkdir(exist_ok=True)
            
            for i in range(file_count):
                content = f"""# Lecture {i+1}
## Introduction
Content for lecture {i+1}.
<!-- SLIDE -->
## Main Points
Key concepts for lecture {i+1}.
"""
                (test_dir / f"lecture_{i+1:03d}.md").write_text(content)
            
            output_dir = test_dir / "output"
            
            # Mock processing to focus on batch coordination overhead
            with patch.object(self.processor.content_splitter, 'split_content') as mock_split:
                mock_split.return_value = ("slides", "notes")
                
                with patch.object(self.processor.quarto_orchestrator, 'generate_slides') as mock_slides:
                    mock_slides.return_value = str(output_dir / "slides.html")
                    
                    with patch.object(self.processor.quarto_orchestrator, 'generate_notes') as mock_notes:
                        mock_notes.return_value = str(output_dir / "notes.pdf")
                        
                        # Create mock output files
                        output_dir.mkdir(exist_ok=True)
                        (output_dir / "slides.html").write_text("mock")
                        (output_dir / "notes.pdf").write_text("mock")
                        
                        # Measure processing time
                        start_time = time.time()
                        result = self.processor.process_directory(test_dir, output_dir)
                        processing_time = time.time() - start_time
                        
                        processing_times.append({
                            'file_count': file_count,
                            'processing_time': processing_time,
                            'files_per_second': file_count / processing_time,
                            'success_rate': result.success_rate
                        })
                        
                        print(f"Files: {file_count}, Time: {processing_time:.3f}s, "
                              f"Rate: {file_count / processing_time:.1f} files/s")
        
        # Check scalability characteristics
        for measurement in processing_times:
            assert measurement['success_rate'] == 100.0
            assert measurement['files_per_second'] > 5  # At least 5 files per second
        
        # Processing should scale reasonably (not exponentially worse)
        time_per_file_10 = processing_times[0]['processing_time'] / processing_times[0]['file_count']
        time_per_file_100 = processing_times[-1]['processing_time'] / processing_times[-1]['file_count']
        
        # Time per file shouldn't increase by more than 3x when scaling from 10 to 100 files
        assert time_per_file_100 / time_per_file_10 < 3.0
    
    def test_parallel_vs_sequential_performance(self):
        """Test performance difference between parallel and sequential processing."""
        # Create test files
        file_count = 20
        for i in range(file_count):
            content = f"""# Lecture {i+1}
Content with some complexity to simulate real processing time.
<!-- SLIDE -->
Slide content {i+1}
<!-- NOTES-ONLY -->
Detailed notes content {i+1}
<!-- ALL -->
"""
            (self.temp_path / f"lecture_{i+1:02d}.md").write_text(content)
        
        output_dir = self.temp_path / "output"
        
        # Mock processing with artificial delay to simulate real work
        def mock_split_with_delay(filepath):
            time.sleep(0.05)  # 50ms processing time per file
            return ("slides content", "notes content")
        
        def mock_generate_with_delay(*args, **kwargs):
            time.sleep(0.02)  # 20ms generation time
            return str(output_dir / "output.html")
        
        # Test sequential processing
        self.config.batch.parallel = False
        
        with patch.object(self.processor.content_splitter, 'split_content', side_effect=mock_split_with_delay):
            with patch.object(self.processor.quarto_orchestrator, 'generate_slides', side_effect=mock_generate_with_delay):
                with patch.object(self.processor.quarto_orchestrator, 'generate_notes', side_effect=mock_generate_with_delay):
                    # Create mock output files
                    output_dir.mkdir(exist_ok=True)
                    (output_dir / "output.html").write_text("mock")
                    
                    start_time = time.time()
                    sequential_result = self.processor.process_directory(self.temp_path, output_dir)
                    sequential_time = time.time() - start_time
        
        # Test parallel processing
        self.config.batch.parallel = True
        self.config.batch.max_workers = 4
        
        with patch.object(self.processor.content_splitter, 'split_content', side_effect=mock_split_with_delay):
            with patch.object(self.processor.quarto_orchestrator, 'generate_slides', side_effect=mock_generate_with_delay):
                with patch.object(self.processor.quarto_orchestrator, 'generate_notes', side_effect=mock_generate_with_delay):
                    start_time = time.time()
                    parallel_result = self.processor.process_directory(self.temp_path, output_dir)
                    parallel_time = time.time() - start_time
        
        print(f"Sequential time: {sequential_time:.3f}s")
        print(f"Parallel time: {parallel_time:.3f}s")
        print(f"Speedup: {sequential_time / parallel_time:.2f}x")
        
        # Both should process all files successfully
        assert sequential_result.successful_files == file_count
        assert parallel_result.successful_files == file_count
        
        # Parallel should be faster (at least 1.5x speedup with 4 workers)
        speedup = sequential_time / parallel_time
        assert speedup > 1.5
    
    def test_memory_efficiency_batch_processing(self):
        """Test memory efficiency during batch processing."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create many files
        file_count = 100
        for i in range(file_count):
            content = f"""# Lecture {i+1}
Content for lecture {i+1} with some mathematical expressions.
$x_{i} = \\sum_{{j=1}}^{i} j^2$
<!-- SLIDE -->
Slide content
<!-- NOTES-ONLY -->
Notes content
<!-- ALL -->
"""
            (self.temp_path / f"lecture_{i+1:03d}.md").write_text(content)
        
        output_dir = self.temp_path / "output"
        
        # Monitor memory during processing
        memory_samples = []
        
        def memory_monitor():
            while not stop_monitoring:
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory - initial_memory)
                time.sleep(0.1)
        
        stop_monitoring = False
        monitor_thread = threading.Thread(target=memory_monitor)
        
        # Mock processing
        with patch.object(self.processor.content_splitter, 'split_content') as mock_split:
            mock_split.return_value = ("slides", "notes")
            
            with patch.object(self.processor.quarto_orchestrator, 'generate_slides') as mock_slides:
                mock_slides.return_value = str(output_dir / "slides.html")
                
                with patch.object(self.processor.quarto_orchestrator, 'generate_notes') as mock_notes:
                    mock_notes.return_value = str(output_dir / "notes.pdf")
                    
                    # Create mock output files
                    output_dir.mkdir(exist_ok=True)
                    (output_dir / "slides.html").write_text("mock")
                    (output_dir / "notes.pdf").write_text("mock")
                    
                    # Start memory monitoring
                    monitor_thread.start()
                    
                    try:
                        result = self.processor.process_directory(self.temp_path, output_dir)
                    finally:
                        stop_monitoring = True
                        monitor_thread.join()
        
        max_memory_used = max(memory_samples) if memory_samples else 0
        avg_memory_used = sum(memory_samples) / len(memory_samples) if memory_samples else 0
        
        print(f"Max memory used: {max_memory_used:.1f} MB")
        print(f"Avg memory used: {avg_memory_used:.1f} MB")
        print(f"Files processed: {result.successful_files}")
        
        # Memory usage should be reasonable
        assert max_memory_used < 500  # Should not use more than 500MB for 100 files
        assert result.successful_files == file_count


class TestQuartoOrchestratorPerformance:
    """Test performance characteristics of Quarto orchestrator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = QuartoOrchestrator()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_command_building_performance(self):
        """Test performance of command building operations."""
        # Test building many commands quickly
        command_count = 1000
        
        start_time = time.time()
        
        for i in range(command_count):
            command = self.orchestrator.command_builder.build_slides_command(
                input_file=f"test_{i}.qmd",
                format="revealjs",
                theme="white"
            )
            assert command.input_file == f"test_{i}.qmd"
        
        building_time = time.time() - start_time
        commands_per_second = command_count / building_time
        
        print(f"Built {command_count} commands in {building_time:.3f}s")
        print(f"Commands per second: {commands_per_second:.0f}")
        
        # Should build commands very quickly
        assert commands_per_second > 1000  # At least 1000 commands per second
    
    def test_multiple_format_generation_performance(self):
        """Test performance when generating multiple output formats."""
        # Create test input file
        test_content = """---
title: "Performance Test"
---

# Test Content

This is test content for performance evaluation.

## Section 1

Content with math: $E = mc^2$

## Section 2

More content here.
"""
        
        input_file = self.temp_path / "perf_test.qmd"
        input_file.write_text(test_content)
        
        formats = ["revealjs", "beamer", "pptx"]
        
        # Mock executor for consistent timing
        with patch.object(self.orchestrator.executor, 'execute_command') as mock_execute:
            def mock_execute_side_effect(command):
                # Simulate processing time based on format
                format_times = {"revealjs": 0.1, "beamer": 0.2, "pptx": 0.15}
                time.sleep(format_times.get(command.output_format, 0.1))
                
                output_file = self.temp_path / f"output.{command.output_format}"
                output_file.write_text(f"Mock {command.output_format} content")
                
                from markdown_slides_generator.core.quarto_orchestrator import QuartoResult
                return QuartoResult(
                    success=True,
                    output_file=str(output_file),
                    stdout=f"Output created: {output_file}",
                    stderr="",
                    return_code=0,
                    execution_time=format_times.get(command.output_format, 0.1)
                )
            
            mock_execute.side_effect = mock_execute_side_effect
            
            # Generate all formats and measure time
            start_time = time.time()
            results = []
            
            for fmt in formats:
                result = self.orchestrator.generate_slides(
                    str(input_file),
                    format=fmt
                )
                results.append(result)
            
            total_time = time.time() - start_time
            
            print(f"Generated {len(formats)} formats in {total_time:.3f}s")
            print(f"Average time per format: {total_time / len(formats):.3f}s")
            
            assert len(results) == len(formats)
            assert total_time < 2.0  # Should complete all formats in under 2 seconds


class TestOverallSystemPerformance:
    """Test overall system performance characteristics."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_performance(self):
        """Test end-to-end performance from markdown to output."""
        # Create a realistic lecture file
        lecture_content = """---
title: "Advanced Calculus - Lecture 5"
author: "Dr. Mathematics"
date: "2024-01-15"
---

# Integration Techniques

## Introduction

Today we'll explore advanced integration techniques including:
- Integration by parts
- Trigonometric substitution  
- Partial fractions

<!-- SLIDE -->

## Integration by Parts

The integration by parts formula is:

$$\\int u \\, dv = uv - \\int v \\, du$$

### Example 1

Let's integrate $\\int x e^x dx$:

<!-- NOTES-ONLY -->

**Detailed Solution:**

Choose $u = x$ and $dv = e^x dx$

Then $du = dx$ and $v = e^x$

Applying the formula:
$$\\int x e^x dx = x e^x - \\int e^x dx = x e^x - e^x + C = e^x(x-1) + C$$

<!-- ALL -->

<!-- SLIDE -->

## Trigonometric Substitution

For integrals involving $\\sqrt{a^2 - x^2}$, use $x = a\\sin\\theta$

### Example 2

$$\\int \\frac{dx}{\\sqrt{4-x^2}}$$

<!-- NOTES-ONLY -->

**Step-by-step solution:**

1. Recognize the form $\\sqrt{a^2 - x^2}$ with $a = 2$
2. Substitute $x = 2\\sin\\theta$, so $dx = 2\\cos\\theta \\, d\\theta$
3. $\\sqrt{4-x^2} = \\sqrt{4-4\\sin^2\\theta} = 2\\cos\\theta$
4. The integral becomes: $\\int \\frac{2\\cos\\theta \\, d\\theta}{2\\cos\\theta} = \\int d\\theta = \\theta + C$
5. Back-substitute: $\\theta = \\arcsin(x/2)$
6. Final answer: $\\arcsin(x/2) + C$

<!-- ALL -->

## Summary

Key integration techniques covered:
1. Integration by parts: $\\int u \\, dv = uv - \\int v \\, du$
2. Trigonometric substitution for radical expressions
3. Choosing appropriate substitution methods

### Practice Problems

Try these problems for homework:
- $\\int x^2 \\ln x \\, dx$
- $\\int \\frac{dx}{\\sqrt{x^2 + 9}}$
- $\\int \\frac{x^2 dx}{x^3 + 1}$
"""
        
        input_file = self.temp_path / "lecture.md"
        input_file.write_text(lecture_content)
        
        # Test complete workflow
        from markdown_slides_generator.core.content_splitter import ContentSplitter
        
        splitter = ContentSplitter()
        
        start_time = time.time()
        
        # Step 1: Process directives
        result = splitter.process_directives(lecture_content)
        directive_time = time.time() - start_time
        
        # Step 2: Generate Quarto files
        slides_path, notes_path = splitter.generate_quarto_files(
            str(input_file), 
            str(self.temp_path / "output")
        )
        quarto_gen_time = time.time() - start_time - directive_time
        
        total_time = time.time() - start_time
        
        print(f"Directive processing: {directive_time:.3f}s")
        print(f"Quarto file generation: {quarto_gen_time:.3f}s")
        print(f"Total end-to-end time: {total_time:.3f}s")
        
        # Performance assertions
        assert directive_time < 1.0  # Directive processing should be fast
        assert quarto_gen_time < 2.0  # File generation should be reasonable
        assert total_time < 3.0  # Complete workflow should finish quickly
        
        # Verify outputs
        assert Path(slides_path).exists()
        assert Path(notes_path).exists()
        
        slides_content = Path(slides_path).read_text()
        notes_content = Path(notes_path).read_text()
        
        # Check content quality
        assert "Integration by parts" in slides_content
        assert "Integration by parts" in notes_content
        assert "Detailed Solution" in notes_content
        assert "Detailed Solution" not in slides_content
    
    def test_stress_test_mixed_workload(self):
        """Test system under mixed workload stress."""
        # Create various types of content
        workloads = [
            ("simple", "# Simple\nBasic content."),
            ("math_heavy", """# Math Heavy
$$\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}$$
$$\\sum_{n=1}^\\infty \\frac{1}{n^2} = \\frac{\\pi^2}{6}$$
$$\\lim_{n \\to \\infty} \\left(1 + \\frac{1}{n}\\right)^n = e$$
"""),
            ("directive_heavy", """# Directive Heavy
<!-- SLIDE-ONLY -->
Slide 1
<!-- NOTES-ONLY -->
Notes 1
<!-- ALL -->
<!-- SLIDE-ONLY -->
Slide 2
<!-- NOTES-ONLY -->
Notes 2
<!-- ALL -->
""" * 50),  # Repeat 50 times
            ("large_content", "# Large\n" + "Content line.\n" * 1000),
        ]
        
        splitter = ContentSplitter()
        processing_times = []
        
        for name, content in workloads:
            start_time = time.time()
            result = splitter.process_directives(content)
            processing_time = time.time() - start_time
            
            processing_times.append({
                'name': name,
                'time': processing_time,
                'content_size': len(content),
                'slides_size': len(result['slides']),
                'notes_size': len(result['notes'])
            })
            
            print(f"{name}: {processing_time:.3f}s, "
                  f"Content: {len(content)/1024:.1f}KB")
        
        # All workloads should complete in reasonable time
        for measurement in processing_times:
            assert measurement['time'] < 5.0  # No single workload should take more than 5s
            assert measurement['slides_size'] > 0
            assert measurement['notes_size'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to see print output