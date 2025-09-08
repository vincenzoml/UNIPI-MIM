"""
Progress Reporter for Batch Processing

Advanced progress reporting with detailed statistics and time estimates.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
from dataclasses import dataclass, field
from collections import deque

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProcessingStats:
    """Statistics for batch processing operations."""
    total_files: int = 0
    processed_files: int = 0
    successful_files: int = 0
    failed_files: int = 0
    skipped_files: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_file: Optional[str] = None
    processing_times: deque = field(default_factory=lambda: deque(maxlen=10))
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.processed_files == 0:
            return 0.0
        return (self.successful_files / self.processed_files) * 100
    
    @property
    def elapsed_time(self) -> timedelta:
        """Calculate elapsed time."""
        if not self.start_time:
            return timedelta(0)
        end_time = self.end_time or datetime.now()
        return end_time - self.start_time
    
    @property
    def average_processing_time(self) -> float:
        """Calculate average processing time per file."""
        if not self.processing_times:
            return 0.0
        return sum(self.processing_times) / len(self.processing_times)
    
    @property
    def estimated_remaining_time(self) -> timedelta:
        """Estimate remaining processing time."""
        if self.processed_files == 0 or self.average_processing_time == 0:
            return timedelta(0)
        
        remaining_files = self.total_files - self.processed_files
        estimated_seconds = remaining_files * self.average_processing_time
        return timedelta(seconds=estimated_seconds)
    
    @property
    def files_per_minute(self) -> float:
        """Calculate processing rate in files per minute."""
        elapsed_minutes = self.elapsed_time.total_seconds() / 60
        if elapsed_minutes == 0:
            return 0.0
        return self.processed_files / elapsed_minutes


class ProgressReporter:
    """
    Advanced progress reporter for batch processing operations.
    
    Provides real-time progress updates, statistics, and time estimates
    with support for parallel processing and detailed error tracking.
    """
    
    def __init__(
        self,
        total_files: int,
        update_callback: Optional[Callable[[ProcessingStats], None]] = None,
        update_interval: float = 1.0
    ):
        self.stats = ProcessingStats(total_files=total_files)
        self.update_callback = update_callback
        self.update_interval = update_interval
        
        self._lock = threading.Lock()
        self._update_thread: Optional[threading.Thread] = None
        self._stop_updates = threading.Event()
        self._last_update = 0.0
        
        logger.debug(f"Progress reporter initialized for {total_files} files")
    
    def start(self) -> None:
        """Start progress reporting."""
        with self._lock:
            self.stats.start_time = datetime.now()
            self._stop_updates.clear()
            
            if self.update_callback:
                self._update_thread = threading.Thread(
                    target=self._update_loop,
                    daemon=True
                )
                self._update_thread.start()
        
        logger.debug("Progress reporting started")
    
    def stop(self) -> None:
        """Stop progress reporting."""
        with self._lock:
            self.stats.end_time = datetime.now()
            self._stop_updates.set()
            
            if self._update_thread and self._update_thread.is_alive():
                self._update_thread.join(timeout=2.0)
        
        # Final update
        if self.update_callback:
            self.update_callback(self.stats)
        
        logger.debug("Progress reporting stopped")
    
    def report_file_start(self, file_path: Path) -> None:
        """Report that processing of a file has started."""
        with self._lock:
            self.stats.current_file = str(file_path)
        
        logger.debug(f"Started processing: {file_path}")
    
    def report_file_success(self, file_path: Path, processing_time: float) -> None:
        """Report successful processing of a file."""
        with self._lock:
            self.stats.processed_files += 1
            self.stats.successful_files += 1
            self.stats.processing_times.append(processing_time)
            self.stats.current_file = None
        
        logger.debug(f"Successfully processed: {file_path} ({processing_time:.2f}s)")
        self._maybe_update()
    
    def report_file_error(
        self,
        file_path: Path,
        error: Exception,
        processing_time: float = 0.0
    ) -> None:
        """Report error processing a file."""
        with self._lock:
            self.stats.processed_files += 1
            self.stats.failed_files += 1
            if processing_time > 0:
                self.stats.processing_times.append(processing_time)
            
            self.stats.errors.append({
                'file': str(file_path),
                'error': str(error),
                'error_type': type(error).__name__,
                'timestamp': datetime.now(),
                'processing_time': processing_time
            })
            self.stats.current_file = None
        
        logger.error(f"Error processing {file_path}: {error}")
        self._maybe_update()
    
    def report_file_skipped(self, file_path: Path, reason: str) -> None:
        """Report that a file was skipped."""
        with self._lock:
            self.stats.processed_files += 1
            self.stats.skipped_files += 1
            self.stats.current_file = None
        
        logger.debug(f"Skipped: {file_path} - {reason}")
        self._maybe_update()
    
    def get_stats(self) -> ProcessingStats:
        """Get current processing statistics."""
        with self._lock:
            return self.stats
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of processing statistics."""
        stats = self.get_stats()
        
        return {
            'total_files': stats.total_files,
            'processed_files': stats.processed_files,
            'successful_files': stats.successful_files,
            'failed_files': stats.failed_files,
            'skipped_files': stats.skipped_files,
            'completion_percentage': stats.completion_percentage,
            'success_rate': stats.success_rate,
            'elapsed_time': str(stats.elapsed_time),
            'estimated_remaining_time': str(stats.estimated_remaining_time),
            'average_processing_time': stats.average_processing_time,
            'files_per_minute': stats.files_per_minute,
            'current_file': stats.current_file,
            'error_count': len(stats.errors),
            'recent_errors': stats.errors[-5:] if stats.errors else []
        }
    
    def format_progress_line(self, include_eta: bool = True) -> str:
        """Format a single-line progress indicator."""
        stats = self.get_stats()
        
        progress_bar = self._create_progress_bar(stats.completion_percentage)
        
        parts = [
            f"{progress_bar}",
            f"{stats.processed_files}/{stats.total_files}",
            f"({stats.completion_percentage:.1f}%)"
        ]
        
        if stats.successful_files > 0:
            parts.append(f"✓{stats.successful_files}")
        
        if stats.failed_files > 0:
            parts.append(f"✗{stats.failed_files}")
        
        if stats.skipped_files > 0:
            parts.append(f"⏭{stats.skipped_files}")
        
        if include_eta and stats.processed_files > 0:
            eta = stats.estimated_remaining_time
            if eta.total_seconds() > 0:
                parts.append(f"ETA: {self._format_duration(eta)}")
        
        if stats.files_per_minute > 0:
            parts.append(f"{stats.files_per_minute:.1f} files/min")
        
        return " | ".join(parts)
    
    def format_detailed_report(self) -> str:
        """Format a detailed progress report."""
        stats = self.get_stats()
        
        lines = [
            "📊 Batch Processing Report",
            "=" * 50,
            f"Total files: {stats.total_files}",
            f"Processed: {stats.processed_files} ({stats.completion_percentage:.1f}%)",
            f"Successful: {stats.successful_files} ({stats.success_rate:.1f}%)",
            f"Failed: {stats.failed_files}",
            f"Skipped: {stats.skipped_files}",
            "",
            f"Elapsed time: {self._format_duration(stats.elapsed_time)}",
            f"Average time per file: {stats.average_processing_time:.2f}s",
            f"Processing rate: {stats.files_per_minute:.1f} files/min"
        ]
        
        if stats.processed_files < stats.total_files:
            eta = stats.estimated_remaining_time
            lines.extend([
                f"Estimated remaining: {self._format_duration(eta)}",
                f"Estimated completion: {(datetime.now() + eta).strftime('%H:%M:%S')}"
            ])
        
        if stats.current_file:
            lines.extend([
                "",
                f"Currently processing: {Path(stats.current_file).name}"
            ])
        
        if stats.errors:
            lines.extend([
                "",
                f"Recent errors ({len(stats.errors[-3:])}):"
            ])
            for error in stats.errors[-3:]:
                lines.append(f"  • {Path(error['file']).name}: {error['error']}")
        
        return "\n".join(lines)
    
    def _update_loop(self) -> None:
        """Background thread for periodic updates."""
        while not self._stop_updates.wait(self.update_interval):
            if self.update_callback:
                try:
                    self.update_callback(self.get_stats())
                except Exception as e:
                    logger.error(f"Error in progress update callback: {e}")
    
    def _maybe_update(self) -> None:
        """Trigger update if enough time has passed."""
        current_time = time.time()
        if current_time - self._last_update >= self.update_interval:
            self._last_update = current_time
            if self.update_callback:
                try:
                    self.update_callback(self.get_stats())
                except Exception as e:
                    logger.error(f"Error in progress update callback: {e}")
    
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Create a text-based progress bar."""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format duration in human-readable format."""
        total_seconds = int(duration.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m {seconds}s"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"


class ConsoleProgressReporter(ProgressReporter):
    """Progress reporter that outputs to console."""
    
    def __init__(
        self,
        total_files: int,
        show_detailed: bool = False,
        update_interval: float = 1.0
    ):
        self.show_detailed = show_detailed
        self._last_line_length = 0
        
        super().__init__(
            total_files=total_files,
            update_callback=self._console_update,
            update_interval=update_interval
        )
    
    def _console_update(self, stats: ProcessingStats) -> None:
        """Update console with current progress."""
        if self.show_detailed:
            # Clear previous output and show detailed report
            print("\033[2J\033[H", end="")  # Clear screen and move to top
            print(self.format_detailed_report())
        else:
            # Show single-line progress
            line = self.format_progress_line()
            
            # Clear previous line
            if self._last_line_length > 0:
                print("\r" + " " * self._last_line_length + "\r", end="")
            
            print(f"\r{line}", end="", flush=True)
            self._last_line_length = len(line)
    
    def stop(self) -> None:
        """Stop progress reporting and print final newline."""
        super().stop()
        if not self.show_detailed:
            print()  # Final newline for single-line progress