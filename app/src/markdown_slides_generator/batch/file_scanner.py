"""
File Scanner for Batch Processing

Intelligent file discovery and filtering for batch operations.
"""

import fnmatch
from pathlib import Path
from typing import List, Set, Optional, Dict, Any, Union, Callable
import os
import stat
from datetime import datetime

from ..utils.logger import get_logger
from ..utils.exceptions import InputError

logger = get_logger(__name__)


class FileScanner:
    """
    Intelligent file scanner for batch processing operations.
    
    Provides advanced file discovery with filtering, exclusion patterns,
    and metadata collection for efficient batch processing.
    """
    
    def __init__(self):
        self.scanned_files: List[Path] = []
        self.excluded_files: List[Path] = []
        self.scan_stats: Dict[str, Any] = {}
    
    def scan_directory(
        self,
        directory: Path,
        pattern: str = '*.md',
        recursive: bool = False,
        exclude_patterns: Optional[List[str]] = None,
        file_filters: Optional[List[Union[str, Callable[[Path], bool]]]] = None,
        max_files: Optional[int] = None,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        modified_after: Optional[datetime] = None,
        modified_before: Optional[datetime] = None
    ) -> List[Path]:
        """
        Scan directory for files matching criteria.
        
        Args:
            directory: Directory to scan
            pattern: File pattern to match (glob style)
            recursive: Whether to scan subdirectories
            exclude_patterns: Patterns to exclude
            file_filters: Additional filter patterns (strings) or callable functions
            max_files: Maximum number of files to return
            min_size: Minimum file size in bytes
            max_size: Maximum file size in bytes
            modified_after: Only include files modified after this date
            modified_before: Only include files modified before this date
            
        Returns:
            List of matching file paths
            
        Raises:
            InputError: If directory doesn't exist or isn't accessible
        """
        if not directory.exists():
            raise InputError(f"Directory not found: {directory}")
        
        if not directory.is_dir():
            raise InputError(f"Path is not a directory: {directory}")
        
        logger.info(f"Scanning directory: {directory}")
        logger.debug(f"Pattern: {pattern}, Recursive: {recursive}")
        
        # Reset state
        self.scanned_files.clear()
        self.excluded_files.clear()
        self.scan_stats = {
            'total_found': 0,
            'excluded_by_pattern': 0,
            'excluded_by_size': 0,
            'excluded_by_date': 0,
            'excluded_by_filter': 0,
            'final_count': 0,
            'scan_time': 0
        }
        
        start_time = datetime.now()
        
        try:
            # Find all matching files
            if recursive:
                found_files = list(directory.rglob(pattern))
            else:
                found_files = list(directory.glob(pattern))
            
            self.scan_stats['total_found'] = len(found_files)
            logger.debug(f"Found {len(found_files)} files matching pattern")
            
            # Apply filters
            filtered_files = self._apply_filters(
                found_files,
                exclude_patterns or [],
                file_filters or [],
                min_size,
                max_size,
                modified_after,
                modified_before
            )
            
            # Apply max files limit
            if max_files and len(filtered_files) > max_files:
                logger.warning(f"Limiting results to {max_files} files (found {len(filtered_files)})")
                filtered_files = filtered_files[:max_files]
            
            self.scanned_files = filtered_files
            self.scan_stats['final_count'] = len(filtered_files)
            self.scan_stats['scan_time'] = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Scan complete: {len(filtered_files)} files selected")
            
            return filtered_files
            
        except PermissionError as e:
            raise InputError(f"Permission denied accessing directory: {directory}", context={'error': str(e)})
        except Exception as e:
            raise InputError(f"Error scanning directory: {e}", context={'directory': str(directory)})
    
    def _apply_filters(
        self,
        files: List[Path],
        exclude_patterns: List[str],
        file_filters: List[Union[str, Callable[[Path], bool]]],
        min_size: Optional[int],
        max_size: Optional[int],
        modified_after: Optional[datetime],
        modified_before: Optional[datetime]
    ) -> List[Path]:
        """Apply various filters to the file list."""
        filtered_files = []
        
        for file_path in files:
            try:
                # Check if file is accessible
                if not file_path.exists() or not file_path.is_file():
                    continue
                
                # Apply exclude patterns
                if self._matches_exclude_patterns(file_path, exclude_patterns):
                    self.excluded_files.append(file_path)
                    self.scan_stats['excluded_by_pattern'] += 1
                    continue
                
                # Apply file filters
                if file_filters and not self._matches_file_filters(file_path, file_filters):
                    self.excluded_files.append(file_path)
                    self.scan_stats['excluded_by_filter'] += 1
                    continue
                
                # Get file stats
                file_stat = file_path.stat()
                
                # Apply size filters
                if min_size and file_stat.st_size < min_size:
                    self.excluded_files.append(file_path)
                    self.scan_stats['excluded_by_size'] += 1
                    continue
                
                if max_size and file_stat.st_size > max_size:
                    self.excluded_files.append(file_path)
                    self.scan_stats['excluded_by_size'] += 1
                    continue
                
                # Apply date filters
                file_mtime = datetime.fromtimestamp(file_stat.st_mtime)
                
                if modified_after and file_mtime < modified_after:
                    self.excluded_files.append(file_path)
                    self.scan_stats['excluded_by_date'] += 1
                    continue
                
                if modified_before and file_mtime > modified_before:
                    self.excluded_files.append(file_path)
                    self.scan_stats['excluded_by_date'] += 1
                    continue
                
                # File passes all filters
                filtered_files.append(file_path)
                
            except (OSError, PermissionError) as e:
                logger.warning(f"Cannot access file {file_path}: {e}")
                continue
        
        return filtered_files
    
    def _matches_exclude_patterns(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if file matches any exclude pattern."""
        for pattern in exclude_patterns:
            # Check against filename
            if fnmatch.fnmatch(file_path.name, pattern):
                return True
            
            # Check against relative path
            if fnmatch.fnmatch(str(file_path), pattern):
                return True
            
            # Check against path components
            for part in file_path.parts:
                if fnmatch.fnmatch(part, pattern):
                    return True
        
        return False
    
    def _matches_file_filters(self, file_path: Path, file_filters: List[Union[str, Callable[[Path], bool]]]) -> bool:
        """Check if file matches all file filters (pattern or callable)."""
        for file_filter in file_filters:
            if callable(file_filter):
                # Handle callable filters
                try:
                    if not file_filter(file_path):
                        return False
                except Exception as e:
                    logger.warning(f"Error applying callable filter to {file_path}: {e}")
                    return False
            else:
                # Handle string pattern filters
                if not (fnmatch.fnmatch(file_path.name, file_filter) or 
                       fnmatch.fnmatch(str(file_path), file_filter)):
                    return False
        
        return True
    
    def get_scan_summary(self) -> Dict[str, Any]:
        """Get summary of the last scan operation."""
        return {
            'files_found': self.scan_stats.get('total_found', 0),
            'files_selected': self.scan_stats.get('final_count', 0),
            'files_excluded': len(self.excluded_files),
            'exclusion_breakdown': {
                'by_pattern': self.scan_stats.get('excluded_by_pattern', 0),
                'by_size': self.scan_stats.get('excluded_by_size', 0),
                'by_date': self.scan_stats.get('excluded_by_date', 0),
                'by_filter': self.scan_stats.get('excluded_by_filter', 0)
            },
            'scan_time_seconds': self.scan_stats.get('scan_time', 0)
        }
    
    def organize_files_by_directory(self, files: Optional[List[Path]] = None) -> Dict[Path, List[Path]]:
        """
        Organize files by their parent directory.
        
        Args:
            files: List of files to organize (uses scanned files if None)
            
        Returns:
            Dictionary mapping directories to lists of files
        """
        if files is None:
            files = self.scanned_files
        
        organized = {}
        for file_path in files:
            parent_dir = file_path.parent
            if parent_dir not in organized:
                organized[parent_dir] = []
            organized[parent_dir].append(file_path)
        
        return organized
    
    def get_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Get metadata for a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file metadata
        """
        try:
            file_stat = file_path.stat()
            
            return {
                'path': str(file_path),
                'name': file_path.name,
                'stem': file_path.stem,
                'suffix': file_path.suffix,
                'size_bytes': file_stat.st_size,
                'size_human': self._format_file_size(file_stat.st_size),
                'modified': datetime.fromtimestamp(file_stat.st_mtime),
                'created': datetime.fromtimestamp(file_stat.st_ctime),
                'permissions': stat.filemode(file_stat.st_mode),
                'is_readable': os.access(file_path, os.R_OK),
                'is_writable': os.access(file_path, os.W_OK)
            }
        except (OSError, PermissionError) as e:
            logger.warning(f"Cannot get metadata for {file_path}: {e}")
            return {
                'path': str(file_path),
                'name': file_path.name,
                'error': str(e)
            }
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def estimate_processing_time(
        self,
        files: Optional[List[Path]] = None,
        time_per_file_seconds: float = 5.0
    ) -> Dict[str, Any]:
        """
        Estimate processing time for the files.
        
        Args:
            files: List of files to estimate for (uses scanned files if None)
            time_per_file_seconds: Estimated processing time per file
            
        Returns:
            Dictionary with time estimates
        """
        if files is None:
            files = self.scanned_files
        
        total_files = len(files)
        total_time_seconds = total_files * time_per_file_seconds
        
        # Calculate total file size
        total_size = 0
        for file_path in files:
            try:
                total_size += file_path.stat().st_size
            except (OSError, PermissionError):
                continue
        
        return {
            'total_files': total_files,
            'estimated_time_seconds': total_time_seconds,
            'estimated_time_human': self._format_duration(total_time_seconds),
            'total_size_bytes': total_size,
            'total_size_human': self._format_file_size(total_size),
            'average_file_size': total_size / total_files if total_files > 0 else 0
        }
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        else:
            hours = seconds / 3600
            return f"{hours:.1f} hours"