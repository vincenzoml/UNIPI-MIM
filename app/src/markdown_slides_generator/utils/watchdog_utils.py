"""
File system watchdog utilities for monitoring markdown files and triggering regeneration.

This module provides a robust file watching system that monitors markdown files
for changes and triggers the generation process automatically.
"""

import time
import threading
from pathlib import Path
from typing import Callable, Optional, Set, List
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .logger import get_logger


logger = get_logger(__name__)


class MarkdownFileHandler(FileSystemEventHandler):
    """Event handler for monitoring markdown file changes."""
    
    def __init__(
        self,
        callback: Callable[[Path], None],
        file_patterns: Optional[List[str]] = None,
        debounce_seconds: float = 1.0
    ):
        """
        Initialize the file handler.
        
        Args:
            callback: Function to call when a relevant file changes
            file_patterns: List of file patterns to monitor (default: ['.md', '.markdown'])
            debounce_seconds: Minimum time between callback calls to prevent rapid firing
        """
        super().__init__()
        self.callback = callback
        self.file_patterns = file_patterns or ['.md', '.markdown']
        self.debounce_seconds = debounce_seconds
        self._last_callback_time: float = 0
        self._callback_lock = threading.Lock()
        
    def _should_process_file(self, file_path: Path) -> bool:
        """Check if a file should trigger the callback."""
        if not file_path.is_file():
            return False
            
        # Check file extension
        if not any(file_path.suffix.lower() == pattern.lower() for pattern in self.file_patterns):
            return False
            
        # Ignore temporary/hidden files
        if file_path.name.startswith('.') or file_path.name.startswith('~'):
            return False
            
        # Ignore files in hidden directories
        if any(part.startswith('.') for part in file_path.parts):
            return False
            
        return True
    
    def _debounced_callback(self, file_path: Path) -> None:
        """Execute callback with debouncing to prevent rapid firing."""
        with self._callback_lock:
            current_time = time.time()
            if current_time - self._last_callback_time >= self.debounce_seconds:
                self._last_callback_time = current_time
                logger.info(f"File change detected: {file_path}")
                try:
                    self.callback(file_path)
                except Exception as e:
                    logger.error(f"Error in watchdog callback: {e}")
            else:
                logger.debug(f"Debouncing file change: {file_path}")
    
    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if self._should_process_file(file_path):
                self._debounced_callback(file_path)
    
    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if self._should_process_file(file_path):
                self._debounced_callback(file_path)


class FileWatcher:
    """
    High-level file watcher for monitoring markdown files.
    
    Provides a simple interface for watching files and directories
    with proper cleanup and error handling.
    """
    
    def __init__(
        self,
        callback: Callable[[Path], None],
        file_patterns: Optional[List[str]] = None,
        debounce_seconds: float = 1.0
    ):
        """
        Initialize the file watcher.
        
        Args:
            callback: Function to call when a relevant file changes
            file_patterns: List of file patterns to monitor
            debounce_seconds: Minimum time between callback calls
        """
        self.callback = callback
        self.file_patterns = file_patterns or ['.md', '.markdown']
        self.debounce_seconds = debounce_seconds
        self.observer = Observer()
        self.event_handler = MarkdownFileHandler(
            callback=self.callback,
            file_patterns=self.file_patterns,
            debounce_seconds=self.debounce_seconds
        )
        self._watching_paths: Set[Path] = set()
        self._is_running = False
    
    def watch_file(self, file_path: Path) -> None:
        """
        Watch a specific file for changes.
        
        Args:
            file_path: Path to the file to watch
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        # Watch the parent directory
        directory = file_path.parent
        self.watch_directory(directory)
    
    def watch_directory(self, directory_path: Path, recursive: bool = False) -> None:
        """
        Watch a directory for changes.
        
        Args:
            directory_path: Path to the directory to watch
            recursive: Whether to watch subdirectories recursively
        """
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not directory_path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")
        
        if directory_path not in self._watching_paths:
            logger.info(f"Watching directory: {directory_path} (recursive: {recursive})")
            self.observer.schedule(
                self.event_handler,
                str(directory_path),
                recursive=recursive
            )
            self._watching_paths.add(directory_path)
    
    def start(self) -> None:
        """Start the file watcher."""
        if not self._watching_paths:
            raise ValueError("No paths to watch. Call watch_file() or watch_directory() first.")
        
        if self._is_running:
            logger.warning("File watcher is already running")
            return
        
        logger.info("Starting file watcher...")
        self.observer.start()
        self._is_running = True
    
    def stop(self) -> None:
        """Stop the file watcher."""
        if not self._is_running:
            return
        
        logger.info("Stopping file watcher...")
        self.observer.stop()
        self.observer.join()
        self._is_running = False
    
    def wait(self) -> None:
        """
        Wait for the watcher to be interrupted (e.g., by Ctrl+C).
        
        This is a blocking call that keeps the watcher running until
        a keyboard interrupt is received.
        """
        if not self._is_running:
            raise ValueError("File watcher is not running")
        
        try:
            logger.info("File watcher is running. Press Ctrl+C to stop.")
            while self._is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        finally:
            self.stop()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.stop()


def create_file_watcher(
    callback: Callable[[Path], None],
    file_patterns: Optional[List[str]] = None,
    debounce_seconds: float = 1.0
) -> FileWatcher:
    """
    Factory function to create a FileWatcher instance.
    
    Args:
        callback: Function to call when a file changes
        file_patterns: List of file patterns to monitor
        debounce_seconds: Minimum time between callback calls
        
    Returns:
        Configured FileWatcher instance
    """
    return FileWatcher(
        callback=callback,
        file_patterns=file_patterns,
        debounce_seconds=debounce_seconds
    )
