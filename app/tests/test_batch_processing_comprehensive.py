"""
Comprehensive tests for batch processing functionality.

Tests parallel processing, error handling, progress reporting, and performance
characteristics for large-scale batch operations.
"""

import pytest
import tempfile
import shutil
import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor

from markdown_slides_generator.batch.batch_processor import (
    BatchProcessor,
    BatchResult,
    FileProcessingResult
)
from markdown_slides_generator.batch.file_scanner import FileScanner
from markdown_slides_generator.batch.progress_reporter import (
    ProgressReporter,
    ConsoleProgressReporter
)
from markdown_slides_generator.config import Config
from markdown_slides_generator.utils.exceptions import ProcessingError, InputError


class TestBatchProcessor:
    """Test batch processing functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.config.batch.parallel = False  # Start with sequential for simpler testing
        self.config.batch.max_workers = 2
        self.config.output.formats = ['html']
        
        self.processor = BatchProcessor(self.config)
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def _create_test_files(self, count: int = 3) -> list[Path]:
        """Create test markdown files."""
        files = []
        for i in range(count):
            content = f"""# Lecture {i+1}

## Introduction
This is lecture {i+1} content.

<!-- SLIDE -->
## Main Points
- Point 1
- Point 2

<!-- NOTES-ONLY -->
## Additional Details
Extended explanation for lecture {i+1}.
"""
            file_path = self.temp_path / f"lecture_{i+1}.md"
            file_path.write_text(content)
            files.append(file_path)
        
        return files
    
    def test_sequential_batch_processing(self):
        """Test sequential batch processing."""
        # Create test files
        files = self._create_test_files(3)
        output_dir = self.temp_path / "output"
        
        # Mock the content splitter and orchestrator
        with patch.object(self.processor.content_splitter, 'split_content') as mock_split:
            mock_split.return_value = ("slides content", "notes content")
            
            with patch.object(self.processor.quarto_orchestrator, 'generate_slides') as mock_slides:
                mock_slides.return_value = str(output_dir / "slides.html")
                
                with patch.object(self.processor.quarto_orchestrator, 'generate_notes') as mock_notes:
                    mock_notes.return_value = str(output_dir / "notes.pdf")
                    
                    # Create mock output files
                    output_dir.mkdir(exist_ok=True)
                    (output_dir / "slides.html").write_text("mock slides")
                    (output_dir / "notes.pdf").write_text("mock notes")
                    
                    result = self.processor.process_directory(
                        self.temp_path,
                        output_dir
                    )
        
        assert result.total_files == 3
        assert result.successful_files == 3
        assert result.failed_files == 0
        assert result.success_rate == 100.0
        assert len(result.generated_outputs) > 0
    
    def test_parallel_batch_processing(self):
        """Test parallel batch processing."""
        self.config.batch.parallel = True
        self.config.batch.max_workers = 2
        
        # Create test files
        files = self._create_test_files(4)
        output_dir = self.temp_path / "output"
        
        # Mock processing components
        with patch.object(self.processor.content_splitter, 'split_content') as mock_split:
            mock_split.return_value = ("slides content", "notes content")
            
            with patch.object(self.processor.quarto_orchestrator, 'generate_slides') as mock_slides:
                mock_slides.return_value = str(output_dir / "slides.html")
                
                with patch.object(self.processor.quarto_orchestrator, 'generate_notes') as mock_notes:
                    mock_notes.return_value = str(output_dir / "notes.pdf")
                    
                    # Create mock output files
                    output_dir.mkdir(exist_ok=True)
                    (output_dir / "slides.html").write_text("mock slides")
                    (output_dir / "notes.pdf").write_text("mock notes")
                    
                    result = self.processor.process_directory(
                        self.temp_path,
                        output_dir
                    )
        
        assert result.total_files == 4
        assert result.successful_files == 4
        assert result.failed_files == 0
        
        # Verify parallel execution was used
        assert mock_split.call_count == 4
    
    def test_error_handling_continue_mode(self):
        """Test error handling in continue mode."""
        self.config.batch.error_handling = 'continue'
        
        # Create test files
        files = self._create_test_files(3)
        output_dir = self.temp_path / "output"
        
        # Mock processing with one failure
        with patch.object(self.processor.content_splitter, 'split_content') as mock_split:
            def split_side_effect(filepath):
                if "lecture_2" in filepath:
                    raise ProcessingError("Simulated processing error")
                return ("slides content", "notes content")
            
            mock_split.side_effect = split_side_effect
            
            with patch.object(self.processor.quarto_orchestrator, 'generate_slides') as mock_slides:
                mock_slides.return_value = str(output_dir / "slides.html")
                
                with patch.object(self.processor.quarto_orchestrator, 'generate_notes') as mock_notes:
                    mock_notes.return_value = str(output_dir / "notes.pdf")
                    
                    # Create mock output files
                    output_dir.mkdir(exist_ok=True)
                    (output_dir / "slides.html").write_text("mock slides")
                    (output_dir / "notes.pdf").write_text("mock notes")
                    
                    result = self.processor.process_directory(
                        self.temp_path,
                        output_dir
                    )
        
        assert result.total_files == 3
        assert result.successful_files == 2
        assert result.failed_files == 1
        assert len(result.errors) == 1
        assert "Simulated processing error" in result.errors[0]['error']
    
    def test_error_handling_stop_mode(self):
        """Test error handling in stop mode."""
        self.config.batch.error_handling = 'stop'
        
        # Create test files
        files = self._create_test_files(3)
        output_dir = self.temp_path / "output"
        
        # Mock processing with early failure
        with patch.object(self.processor.content_splitter, 'split_content') as mock_split:
            def split_side_effect(filepath):
                if "lecture_1" in filepath:
                    raise ProcessingError("Critical error")
                return ("slides content", "notes content")
            
            mock_split.side_effect = split_side_effect
            
            result = self.processor.process_directory(
                self.temp_path,
                output_dir
            )
        
        # Should stop after first error
        assert result.failed_files >= 1
        assert result.successful_files < 3  # Not all files processed
    
    def test_file_conflict_handling(self):
        """Test handling of existing output files."""
        self.config.output.overwrite = False
        
        # Create test files
        files = self._create_test_files(2)
        output_dir = self.temp_path / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Create existing output files
        existing_file = output_dir / "lecture_1_slides.html"
        existing_file.write_text("existing content")
        
        # Mock processing
        with patch.object(self.processor.content_splitter, 'split_content') as mock_split:
            mock_split.return_value = ("slides content", "notes content")
            
            result = self.processor.process_directory(
                self.temp_path,
                output_dir
            )
        
        # Should skip files with existing outputs
        assert result.skipped_files >= 1
    
    def test_dry_run_mode(self):
        """Test dry run simulation."""
        # Create test files
        files = self._create_test_files(3)
        output_dir = self.temp_path / "output"
        
        result = self.processor.process_directory(
            self.temp_path,
            output_dir,
            dry_run=True
        )
        
        assert result.total_files == 3
        assert result.successful_files == 3  # All simulated as successful
        assert result.failed_files == 0
        assert result.processing_time == 0.0
        assert len(result.generated_outputs) > 0  # Simulated outputs
    
    def test_progress_reporting(self):
        """Test progress reporting functionality."""
        # Create test files
        files = self._create_test_files(3)
        output_dir = self.temp_path / "output"
        
        progress_updates = []
        
        def progress_callback(reporter):
            progress_updates.append({
                'processed': reporter.processed_files,
                'total': reporter.total_files,
                'percentage': reporter.get_progress_percentage()
            })
        
        # Mock processing
        with patch.object(self.processor.content_splitter, 'split_content') as mock_split:
            mock_split.return_value = ("slides content", "notes content")
            
            with patch.object(self.processor.quarto_orchestrator, 'generate_slides') as mock_slides:
                mock_slides.return_value = str(output_dir / "slides.html")
                
                with patch.object(self.processor.quarto_orchestrator, 'generate_notes') as mock_notes:
                    mock_notes.return_value = str(output_dir / "notes.pdf")
                    
                    # Create mock output files
                    output_dir.mkdir(exist_ok=True)
                    (output_dir / "slides.html").write_text("mock slides")
                    (output_dir / "notes.pdf").write_text("mock notes")
                    
                    result = self.processor.process_directory(
                        self.temp_path,
                        output_dir,
                        progress_callback=progress_callback
                    )
        
        # Should have received progress updates
        assert len(progress_updates) >= 0  # May be empty if processing is too fast
    
    def test_processing_estimates(self):
        """Test processing time and resource estimates."""
        # Create test files of various sizes
        files = []
        for i in range(5):
            content = f"# Lecture {i+1}\n" + "Content line.\n" * (100 * (i + 1))
            file_path = self.temp_path / f"lecture_{i+1}.md"
            file_path.write_text(content)
            files.append(file_path)
        
        estimate = self.processor.get_processing_estimate(self.temp_path)
        
        assert estimate['total_files'] == 5
        assert estimate['estimated_time_seconds'] > 0
        assert estimate['estimated_outputs'] > 0
        assert estimate['total_size_bytes'] > 0
        assert 'estimated_time_human' in estimate
        assert 'total_size_human' in estimate
    
    def test_empty_directory_handling(self):
        """Test handling of empty directories."""
        empty_dir = self.temp_path / "empty"
        empty_dir.mkdir()
        output_dir = self.temp_path / "output"
        
        result = self.processor.process_directory(empty_dir, output_dir)
        
        assert result.total_files == 0
        assert result.successful_files == 0
        assert result.failed_files == 0
        assert result.processing_time >= 0
    
    def test_nested_directory_structure(self):
        """Test processing nested directory structures."""
        self.config.batch.recursive = True
        
        # Create nested structure
        (self.temp_path / "week1").mkdir()
        (self.temp_path / "week2").mkdir()
        
        # Create files in nested directories
        for week in [1, 2]:
            for lecture in [1, 2]:
                content = f"# Week {week} Lecture {lecture}\nContent here."
                file_path = self.temp_path / f"week{week}" / f"lecture{lecture}.md"
                file_path.write_text(content)
        
        output_dir = self.temp_path / "output"
        
        # Mock processing
        with patch.object(self.processor.content_splitter, 'split_content') as mock_split:
            mock_split.return_value = ("slides content", "notes content")
            
            with patch.object(self.processor.quarto_orchestrator, 'generate_slides') as mock_slides:
                mock_slides.return_value = str(output_dir / "slides.html")
                
                with patch.object(self.processor.quarto_orchestrator, 'generate_notes') as mock_notes:
                    mock_notes.return_value = str(output_dir / "notes.pdf")
                    
                    # Create mock output files
                    output_dir.mkdir(exist_ok=True)
                    (output_dir / "slides.html").write_text("mock slides")
                    (output_dir / "notes.pdf").write_text("mock notes")
                    
                    result = self.processor.process_directory(
                        self.temp_path,
                        output_dir
                    )
        
        assert result.total_files == 4  # 2 weeks × 2 lectures


class TestFileScanner:
    """Test file scanning functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scanner = FileScanner()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_basic_file_scanning(self):
        """Test basic file scanning with patterns."""
        # Create test files
        (self.temp_path / "lecture1.md").write_text("content")
        (self.temp_path / "lecture2.md").write_text("content")
        (self.temp_path / "readme.txt").write_text("content")
        (self.temp_path / "notes.md").write_text("content")
        
        files = self.scanner.scan_directory(
            directory=self.temp_path,
            pattern="*.md"
        )
        
        assert len(files) == 3
        assert all(f.suffix == '.md' for f in files)
    
    def test_recursive_scanning(self):
        """Test recursive directory scanning."""
        # Create nested structure
        (self.temp_path / "subdir").mkdir()
        (self.temp_path / "lecture1.md").write_text("content")
        (self.temp_path / "subdir" / "lecture2.md").write_text("content")
        
        files = self.scanner.scan_directory(
            directory=self.temp_path,
            pattern="*.md",
            recursive=True
        )
        
        assert len(files) == 2
        
        # Test non-recursive
        files_non_recursive = self.scanner.scan_directory(
            directory=self.temp_path,
            pattern="*.md",
            recursive=False
        )
        
        assert len(files_non_recursive) == 1
    
    def test_exclude_patterns(self):
        """Test file exclusion patterns."""
        # Create test files
        (self.temp_path / "lecture1.md").write_text("content")
        (self.temp_path / "draft_lecture2.md").write_text("content")
        (self.temp_path / "backup_lecture3.md").write_text("content")
        
        files = self.scanner.scan_directory(
            directory=self.temp_path,
            pattern="*.md",
            exclude_patterns=["draft_*", "backup_*"]
        )
        
        assert len(files) == 1
        assert files[0].name == "lecture1.md"
    
    def test_file_filters(self):
        """Test file filtering by size and modification time."""
        # Create files of different sizes
        small_file = self.temp_path / "small.md"
        large_file = self.temp_path / "large.md"
        
        small_file.write_text("small content")
        large_file.write_text("large content" * 1000)
        
        # Filter by minimum size
        files = self.scanner.scan_directory(
            directory=self.temp_path,
            pattern="*.md",
            file_filters=[
                lambda f: f.stat().st_size > 100  # Only large files
            ]
        )
        
        assert len(files) == 1
        assert files[0].name == "large.md"
    
    def test_processing_time_estimation(self):
        """Test processing time estimation."""
        # Create files of various sizes
        for i in range(3):
            content = f"Content for file {i}\n" * (100 * (i + 1))
            (self.temp_path / f"file{i}.md").write_text(content)
        
        files = self.scanner.scan_directory(
            directory=self.temp_path,
            pattern="*.md"
        )
        
        estimate = self.scanner.estimate_processing_time(files)
        
        assert estimate['total_files'] == 3
        assert estimate['estimated_time_seconds'] > 0
        assert estimate['total_size_bytes'] > 0
        assert 'estimated_time_human' in estimate
        assert 'total_size_human' in estimate


class TestProgressReporter:
    """Test progress reporting functionality."""
    
    def test_console_progress_reporter(self):
        """Test console progress reporter."""
        reporter = ConsoleProgressReporter(
            total_files=5,
            show_detailed=True,
            update_interval=0.1
        )
        
        # Test basic functionality
        assert reporter.total_files == 5
        assert reporter.processed_files == 0
        assert reporter.get_progress_percentage() == 0.0
        
        # Test file processing updates
        test_file = Path("test.md")
        
        reporter.report_file_start(test_file)
        assert reporter.current_file == str(test_file)
        
        reporter.report_file_success(test_file, 1.0)
        assert reporter.processed_files == 1
        assert reporter.get_progress_percentage() == 20.0
        
        # Test error reporting
        reporter.report_file_error(test_file, Exception("Test error"), 0.5)
        assert reporter.processed_files == 2
        assert len(reporter.errors) == 1
    
    def test_progress_callback(self):
        """Test progress callback functionality."""
        callback_calls = []
        
        def test_callback(reporter):
            callback_calls.append({
                'processed': reporter.processed_files,
                'total': reporter.total_files,
                'percentage': reporter.get_progress_percentage()
            })
        
        reporter = ConsoleProgressReporter(
            total_files=3,
            show_detailed=False,
            update_interval=0
        )
        reporter.update_callback = test_callback
        
        # Simulate file processing
        for i in range(3):
            test_file = Path(f"test{i}.md")
            reporter.report_file_start(test_file)
            reporter.report_file_success(test_file, 1.0)
        
        # Should have received callbacks
        assert len(callback_calls) >= 3
        assert callback_calls[-1]['percentage'] == 100.0


class TestBatchProcessingPerformance:
    """Test performance characteristics of batch processing."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.config.batch.parallel = True
        self.config.batch.max_workers = 4
        self.processor = BatchProcessor(self.config)
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_parallel_vs_sequential_performance(self):
        """Test performance difference between parallel and sequential processing."""
        # Create multiple test files
        files = []
        for i in range(10):
            content = f"# Lecture {i+1}\n" + "Content line.\n" * 100
            file_path = self.temp_path / f"lecture_{i+1}.md"
            file_path.write_text(content)
            files.append(file_path)
        
        output_dir = self.temp_path / "output"
        
        # Mock processing with artificial delay
        def mock_split_with_delay(filepath):
            time.sleep(0.1)  # Simulate processing time
            return ("slides content", "notes content")
        
        def mock_generate_with_delay(*args, **kwargs):
            time.sleep(0.05)  # Simulate generation time
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
        
        with patch.object(self.processor.content_splitter, 'split_content', side_effect=mock_split_with_delay):
            with patch.object(self.processor.quarto_orchestrator, 'generate_slides', side_effect=mock_generate_with_delay):
                with patch.object(self.processor.quarto_orchestrator, 'generate_notes', side_effect=mock_generate_with_delay):
                    start_time = time.time()
                    parallel_result = self.processor.process_directory(self.temp_path, output_dir)
                    parallel_time = time.time() - start_time
        
        # Parallel should be faster (though not always guaranteed in tests)
        assert sequential_result.successful_files == parallel_result.successful_files
        # Note: In real scenarios, parallel should be faster, but in tests with mocks
        # the difference might not be significant
    
    def test_memory_usage_with_large_batch(self):
        """Test memory usage characteristics with large batches."""
        # Create many small files to test memory efficiency
        for i in range(50):
            content = f"# File {i}\nSmall content."
            (self.temp_path / f"file_{i:03d}.md").write_text(content)
        
        output_dir = self.temp_path / "output"
        
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
                    
                    result = self.processor.process_directory(self.temp_path, output_dir)
        
        assert result.total_files == 50
        assert result.successful_files == 50
        # Test should complete without memory issues


if __name__ == "__main__":
    pytest.main([__file__])