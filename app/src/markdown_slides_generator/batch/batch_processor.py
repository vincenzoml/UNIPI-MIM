"""
Batch Processor for Markdown Slides Generator

Advanced batch processing with parallel execution, intelligent error handling,
and comprehensive progress reporting.
"""

import time
import concurrent.futures
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from datetime import datetime

from ..utils.logger import get_logger
from ..utils.exceptions import ProcessingError, InputError
from ..config import Config
from ..core.content_splitter import ContentSplitter
from ..core.quarto_orchestrator import QuartoOrchestrator
from .file_scanner import FileScanner
from .progress_reporter import ProgressReporter, ConsoleProgressReporter

logger = get_logger(__name__)


@dataclass
class BatchResult:
    """Result of batch processing operation."""
    total_files: int
    successful_files: int
    failed_files: int
    skipped_files: int
    generated_outputs: List[str]
    processing_time: float
    errors: List[Dict[str, Any]]
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.successful_files / self.total_files) * 100


@dataclass
class FileProcessingResult:
    """Result of processing a single file."""
    file_path: Path
    status: str  # 'success', 'error', 'skipped'
    generated_files: List[str]
    processing_time: float
    error: Optional[Exception] = None
    skip_reason: Optional[str] = None


class BatchProcessor:
    """
    Advanced batch processor for markdown files.
    
    Provides parallel processing, intelligent error handling, progress reporting,
    and file conflict resolution for efficient batch operations.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.file_scanner = FileScanner()
        self.content_splitter = ContentSplitter()
        self.quarto_orchestrator = QuartoOrchestrator()
        
        # Processing state
        self._processing_lock = threading.Lock()
        self._processed_files: Dict[str, FileProcessingResult] = {}
        
        logger.debug("Batch processor initialized")
    
    def process_directory(
        self,
        input_dir: Path,
        output_dir: Path,
        progress_callback: Optional[Callable[[ProgressReporter], None]] = None,
        dry_run: bool = False
    ) -> BatchResult:
        """
        Process all files in a directory according to configuration.
        
        Args:
            input_dir: Directory containing markdown files
            output_dir: Directory for generated outputs
            progress_callback: Optional callback for progress updates
            dry_run: If True, only simulate processing
            
        Returns:
            BatchResult with processing statistics and results
            
        Raises:
            InputError: If input directory is invalid
            ProcessingError: If batch processing fails
        """
        logger.info(f"Starting batch processing: {input_dir} -> {output_dir}")
        
        start_time = time.time()
        
        try:
            # Scan for files
            files = self._scan_files(input_dir)
            
            if not files:
                logger.warning(f"No files found matching criteria in {input_dir}")
                return BatchResult(
                    total_files=0,
                    successful_files=0,
                    failed_files=0,
                    skipped_files=0,
                    generated_outputs=[],
                    processing_time=0.0,
                    errors=[]
                )
            
            logger.info(f"Found {len(files)} files to process")
            
            if dry_run:
                return self._simulate_processing(files, output_dir)
            
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize progress reporter
            progress_reporter = ConsoleProgressReporter(
                total_files=len(files),
                show_detailed=False,
                update_interval=self.config.batch.progress_reporting and 1.0 or 0
            )
            
            if progress_callback:
                progress_reporter.update_callback = progress_callback
            
            # Process files
            results = self._process_files(files, input_dir, output_dir, progress_reporter)
            
            # Calculate final statistics
            processing_time = time.time() - start_time
            
            successful_files = sum(1 for r in results if r.status == 'success')
            failed_files = sum(1 for r in results if r.status == 'error')
            skipped_files = sum(1 for r in results if r.status == 'skipped')
            
            generated_outputs = []
            errors = []
            
            for result in results:
                if result.status == 'success':
                    generated_outputs.extend(result.generated_files)
                elif result.status == 'error' and result.error:
                    errors.append({
                        'file': str(result.file_path),
                        'error': str(result.error),
                        'error_type': type(result.error).__name__,
                        'processing_time': result.processing_time
                    })
            
            batch_result = BatchResult(
                total_files=len(files),
                successful_files=successful_files,
                failed_files=failed_files,
                skipped_files=skipped_files,
                generated_outputs=generated_outputs,
                processing_time=processing_time,
                errors=errors
            )
            
            logger.info(f"Batch processing complete: {successful_files}/{len(files)} successful")
            
            return batch_result
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise ProcessingError(f"Batch processing failed: {e}")
    
    def _scan_files(self, input_dir: Path) -> List[Path]:
        """Scan directory for files to process."""
        return self.file_scanner.scan_directory(
            directory=input_dir,
            pattern=self.config.batch.pattern,
            recursive=self.config.batch.recursive,
            exclude_patterns=self.config.batch.exclude_patterns,
            file_filters=self.config.batch.file_filters
        )
    
    def _simulate_processing(self, files: List[Path], output_dir: Path) -> BatchResult:
        """Simulate processing for dry run."""
        logger.info("Simulating batch processing (dry run)")
        
        simulated_outputs = []
        for file_path in files:
            # Simulate output file names
            for fmt in self.config.output.formats:
                slides_output = output_dir / f"{file_path.stem}_slides.{fmt}"
                notes_output = output_dir / f"{file_path.stem}_notes.{fmt}"
                simulated_outputs.extend([str(slides_output), str(notes_output)])
        
        return BatchResult(
            total_files=len(files),
            successful_files=len(files),  # Assume all would succeed
            failed_files=0,
            skipped_files=0,
            generated_outputs=simulated_outputs,
            processing_time=0.0,
            errors=[]
        )
    
    def _process_files(
        self,
        files: List[Path],
        input_dir: Path,
        output_dir: Path,
        progress_reporter: ProgressReporter
    ) -> List[FileProcessingResult]:
        """Process files with parallel or sequential execution."""
        progress_reporter.start()
        
        try:
            if self.config.batch.parallel and len(files) > 1:
                return self._process_files_parallel(files, input_dir, output_dir, progress_reporter)
            else:
                return self._process_files_sequential(files, input_dir, output_dir, progress_reporter)
        finally:
            progress_reporter.stop()
    
    def _process_files_parallel(
        self,
        files: List[Path],
        input_dir: Path,
        output_dir: Path,
        progress_reporter: ProgressReporter
    ) -> List[FileProcessingResult]:
        """Process files in parallel using thread pool."""
        logger.info(f"Processing {len(files)} files with {self.config.batch.max_workers} workers")
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.batch.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(
                    self._process_single_file,
                    file_path,
                    input_dir,
                    output_dir,
                    progress_reporter
                ): file_path
                for file_path in files
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_file):
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Handle errors based on configuration
                    if result.status == 'error' and self.config.batch.error_handling == 'stop':
                        logger.error("Stopping batch processing due to error")
                        # Cancel remaining tasks
                        for remaining_future in future_to_file:
                            if not remaining_future.done():
                                remaining_future.cancel()
                        break
                        
                except Exception as e:
                    file_path = future_to_file[future]
                    logger.error(f"Unexpected error processing {file_path}: {e}")
                    
                    result = FileProcessingResult(
                        file_path=file_path,
                        status='error',
                        generated_files=[],
                        processing_time=0.0,
                        error=e
                    )
                    results.append(result)
                    progress_reporter.report_file_error(file_path, e)
        
        return results
    
    def _process_files_sequential(
        self,
        files: List[Path],
        input_dir: Path,
        output_dir: Path,
        progress_reporter: ProgressReporter
    ) -> List[FileProcessingResult]:
        """Process files sequentially."""
        logger.info(f"Processing {len(files)} files sequentially")
        
        results = []
        
        for file_path in files:
            try:
                result = self._process_single_file(file_path, input_dir, output_dir, progress_reporter)
                results.append(result)
                
                # Handle errors based on configuration
                if result.status == 'error' and self.config.batch.error_handling == 'stop':
                    logger.error("Stopping batch processing due to error")
                    break
                    
            except Exception as e:
                logger.error(f"Unexpected error processing {file_path}: {e}")
                
                result = FileProcessingResult(
                    file_path=file_path,
                    status='error',
                    generated_files=[],
                    processing_time=0.0,
                    error=e
                )
                results.append(result)
                progress_reporter.report_file_error(file_path, e)
                
                if self.config.batch.error_handling == 'stop':
                    break
        
        return results
    
    def _process_single_file(
        self,
        file_path: Path,
        input_dir: Path,
        output_dir: Path,
        progress_reporter: ProgressReporter
    ) -> FileProcessingResult:
        """Process a single markdown file."""
        start_time = time.time()
        
        progress_reporter.report_file_start(file_path)
        
        try:
            # Calculate relative output directory
            rel_path = file_path.relative_to(input_dir).parent
            file_output_dir = output_dir / rel_path
            
            # Check for existing files if not overwriting
            if not self.config.output.overwrite:
                existing_files = self._check_existing_files(file_path, file_output_dir)
                if existing_files:
                    processing_time = time.time() - start_time
                    progress_reporter.report_file_skipped(
                        file_path,
                        f"Output files already exist: {', '.join(f.name for f in existing_files)}"
                    )
                    return FileProcessingResult(
                        file_path=file_path,
                        status='skipped',
                        generated_files=[],
                        processing_time=processing_time,
                        skip_reason="Files already exist"
                    )
            
            # Create output directory
            file_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Process the markdown file
            slides_content, notes_content = self.content_splitter.split_content(str(file_path))
            
            # Create temporary files
            slides_file = file_output_dir / f"{file_path.stem}_slides.qmd"
            notes_file_path = file_output_dir / f"{file_path.stem}_notes.qmd"
            
            with open(slides_file, 'w', encoding='utf-8') as f:
                f.write(slides_content)
            with open(notes_file_path, 'w', encoding='utf-8') as f:
                f.write(notes_content)
            
            generated_files = []
            
            # Generate slides for each format
            for fmt in self.config.output.formats:
                try:
                    output_file = self.quarto_orchestrator.generate_slides(
                        str(slides_file), fmt, None, self.config.slides.theme
                    )
                    generated_files.append(output_file)
                except Exception as e:
                    logger.error(f"Error generating {fmt} slides for {file_path}: {e}")
                    if self.config.batch.error_handling == 'stop':
                        raise
            
            # Generate notes (use configured notes formats, default to pdf)
            try:
                notes_formats = getattr(self.config.notes, 'formats', None) or ['pdf']
                notes_primary = notes_formats[0]
                notes_output = self.quarto_orchestrator.generate_notes(
                    str(notes_file_path), notes_primary
                )
                generated_files.append(notes_output)
            except Exception as e:
                logger.error(f"Error generating notes for {file_path}: {e}")
                if self.config.batch.error_handling == 'stop':
                    raise
            
            # Clean up temporary files
            if slides_file.exists():
                slides_file.unlink()
            if notes_file_path.exists():
                notes_file_path.unlink()
            
            processing_time = time.time() - start_time
            progress_reporter.report_file_success(file_path, processing_time)
            
            return FileProcessingResult(
                file_path=file_path,
                status='success',
                generated_files=generated_files,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            progress_reporter.report_file_error(file_path, e, processing_time)
            
            return FileProcessingResult(
                file_path=file_path,
                status='error',
                generated_files=[],
                processing_time=processing_time,
                error=e
            )
    
    def _check_existing_files(self, file_path: Path, output_dir: Path) -> List[Path]:
        """Check for existing output files."""
        existing_files = []
        
        for fmt in self.config.output.formats:
            potential_files = [
                output_dir / f"{file_path.stem}_slides.{fmt}",
                output_dir / f"{file_path.stem}_notes.{fmt}",
            ]
            existing_files.extend([f for f in potential_files if f.exists()])
        
        return existing_files
    
    def get_processing_estimate(self, input_dir: Path) -> Dict[str, Any]:
        """
        Get processing time and resource estimates for a directory.
        
        Args:
            input_dir: Directory to analyze
            
        Returns:
            Dictionary with processing estimates
        """
        try:
            files = self._scan_files(input_dir)
            
            if not files:
                return {
                    'total_files': 0,
                    'estimated_time': 0,
                    'estimated_outputs': 0,
                    'total_size': 0
                }
            
            # Get file scanner estimates
            scanner_estimate = self.file_scanner.estimate_processing_time(files)
            
            # Calculate output estimates
            outputs_per_file = len(self.config.output.formats) + 1  # slides + notes
            total_outputs = len(files) * outputs_per_file
            
            return {
                'total_files': len(files),
                'estimated_time_seconds': scanner_estimate['estimated_time_seconds'],
                'estimated_time_human': scanner_estimate['estimated_time_human'],
                'estimated_outputs': total_outputs,
                'total_size_bytes': scanner_estimate['total_size_bytes'],
                'total_size_human': scanner_estimate['total_size_human'],
                'parallel_processing': self.config.batch.parallel,
                'max_workers': self.config.batch.max_workers if self.config.batch.parallel else 1,
                'output_formats': self.config.output.formats
            }
            
        except Exception as e:
            logger.error(f"Error calculating processing estimate: {e}")
            return {
                'error': str(e)
            }