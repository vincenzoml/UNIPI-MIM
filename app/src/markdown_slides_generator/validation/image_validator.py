"""
Image Validator - Validates and optimizes images and media files.

Checks for missing images, validates file formats, analyzes file sizes,
and provides optimization suggestions for better presentation performance.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import mimetypes

from ..utils.logger import get_logger
from ..utils.exceptions import handle_exception

logger = get_logger(__name__)


@dataclass
class ImageInfo:
    """Information about an image file."""
    path: str
    alt_text: str
    exists: bool
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    dimensions: Optional[Tuple[int, int]] = None
    is_optimized: bool = False


@dataclass
class ImageValidationResult:
    """Result of image validation."""
    total_images: int
    valid_images: int
    missing_images: int
    oversized_images: int
    images_without_alt: int
    optimization_suggestions: List[str]
    image_info: List[ImageInfo]
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_images == 0:
            return 100.0
        return (self.valid_images / self.total_images) * 100.0


class ImageValidator:
    """
    Comprehensive image validation and optimization system.
    
    Validates image files, checks accessibility requirements,
    analyzes file sizes, and provides optimization suggestions.
    """
    
    # Image patterns
    MARKDOWN_IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    HTML_IMAGE_PATTERN = re.compile(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>')
    
    # File size thresholds (in bytes)
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    OPTIMAL_IMAGE_SIZE = 1 * 1024 * 1024  # 1MB
    WARNING_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB
    
    # Supported formats
    SUPPORTED_FORMATS = {
        '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp',
        '.bmp', '.tiff', '.tif', '.ico'
    }
    
    # Optimal formats for different use cases
    OPTIMAL_FORMATS = {
        'photos': ['.jpg', '.jpeg', '.webp'],
        'graphics': ['.png', '.svg', '.webp'],
        'animations': ['.gif', '.webp'],
        'icons': ['.svg', '.png', '.ico']
    }
    
    def __init__(self):
        self.optimization_suggestions: List[str] = []
    
    @handle_exception
    def validate_images(self, content: str, base_path: Optional[Path] = None) -> ImageValidationResult:
        """
        Validate all images in the given content.
        
        Args:
            content: Markdown content to check
            base_path: Base path for resolving relative image paths
            
        Returns:
            ImageValidationResult with validation results
        """
        logger.info("Starting comprehensive image validation")
        self.optimization_suggestions = []
        
        # Extract all images from content
        images = self._extract_images(content)
        logger.info(f"Found {len(images)} images to validate")
        
        if not images:
            return ImageValidationResult(
                total_images=0,
                valid_images=0,
                missing_images=0,
                oversized_images=0,
                images_without_alt=0,
                optimization_suggestions=[],
                image_info=[]
            )
        
        # Validate each image
        image_info = []
        for alt_text, image_path in images:
            info = self._validate_single_image(alt_text, image_path, base_path)
            image_info.append(info)
        
        # Analyze results
        valid_count = sum(1 for info in image_info if info.exists)
        missing_count = sum(1 for info in image_info if not info.exists)
        oversized_count = sum(1 for info in image_info 
                            if info.file_size and info.file_size > self.WARNING_IMAGE_SIZE)
        no_alt_count = sum(1 for info in image_info if not info.alt_text.strip())
        
        result = ImageValidationResult(
            total_images=len(image_info),
            valid_images=valid_count,
            missing_images=missing_count,
            oversized_images=oversized_count,
            images_without_alt=no_alt_count,
            optimization_suggestions=self.optimization_suggestions.copy(),
            image_info=image_info
        )
        
        logger.info(f"Image validation complete: {valid_count} valid, {missing_count} missing, "
                   f"{oversized_count} oversized ({result.success_rate:.1f}% success rate)")
        
        return result
    
    def _extract_images(self, content: str) -> List[Tuple[str, str]]:
        """
        Extract all images from markdown content.
        
        Returns:
            List of (alt_text, image_path) tuples
        """
        images = []
        
        # Extract markdown images
        markdown_images = self.MARKDOWN_IMAGE_PATTERN.findall(content)
        images.extend(markdown_images)
        
        # Extract HTML images
        html_images = self.HTML_IMAGE_PATTERN.findall(content)
        images.extend([('', path) for path in html_images])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_images = []
        for alt_text, path in images:
            if path not in seen:
                seen.add(path)
                unique_images.append((alt_text, path))
        
        return unique_images
    
    def _validate_single_image(self, alt_text: str, image_path: str, base_path: Optional[Path]) -> ImageInfo:
        """Validate a single image."""
        # Skip URLs (external images)
        if image_path.startswith(('http://', 'https://', 'data:')):
            return ImageInfo(
                path=image_path,
                alt_text=alt_text,
                exists=True,  # Assume external images exist
                is_optimized=True  # Can't optimize external images
            )
        
        # Resolve relative paths
        if base_path and not Path(image_path).is_absolute():
            full_path = base_path / image_path
        else:
            full_path = Path(image_path)
        
        # Check if file exists
        exists = full_path.exists()
        
        info = ImageInfo(
            path=image_path,
            alt_text=alt_text,
            exists=exists
        )
        
        if not exists:
            self.optimization_suggestions.append(
                f"Missing image file: {image_path}"
            )
            return info
        
        # Get file information
        try:
            stat = full_path.stat()
            info.file_size = stat.st_size
            info.mime_type = mimetypes.guess_type(str(full_path))[0]
            
            # Check file format
            suffix = full_path.suffix.lower()
            if suffix not in self.SUPPORTED_FORMATS:
                self.optimization_suggestions.append(
                    f"Unsupported image format: {image_path} ({suffix})"
                )
            
            # Check file size
            if info.file_size > self.MAX_IMAGE_SIZE:
                self.optimization_suggestions.append(
                    f"Image too large: {image_path} ({info.file_size / 1024 / 1024:.1f}MB) "
                    f"- consider compressing or resizing"
                )
            elif info.file_size > self.WARNING_IMAGE_SIZE:
                self.optimization_suggestions.append(
                    f"Large image file: {image_path} ({info.file_size / 1024 / 1024:.1f}MB) "
                    f"- consider optimizing for better performance"
                )
            
            # Check alt text
            if not alt_text.strip():
                self.optimization_suggestions.append(
                    f"Missing alt text for accessibility: {image_path}"
                )
            elif len(alt_text) > 125:
                self.optimization_suggestions.append(
                    f"Alt text too long: {image_path} ({len(alt_text)} chars) "
                    f"- consider shortening for better accessibility"
                )
            
            # Get image dimensions if possible
            try:
                dimensions = self._get_image_dimensions(full_path)
                info.dimensions = dimensions
                
                if dimensions:
                    width, height = dimensions
                    # Check for very large dimensions
                    if width > 4000 or height > 4000:
                        self.optimization_suggestions.append(
                            f"Very high resolution image: {image_path} ({width}x{height}) "
                            f"- consider resizing for web use"
                        )
                    elif width > 2000 or height > 2000:
                        self.optimization_suggestions.append(
                            f"High resolution image: {image_path} ({width}x{height}) "
                            f"- may benefit from resizing for faster loading"
                        )
            except Exception:
                pass  # Dimensions not critical
            
            # Suggest format optimizations
            self._suggest_format_optimization(full_path, info)
            
            # Mark as optimized if it meets criteria
            info.is_optimized = (
                info.file_size <= self.OPTIMAL_IMAGE_SIZE and
                suffix in self.SUPPORTED_FORMATS and
                bool(alt_text.strip()) and
                len(alt_text) <= 125
            )
            
        except OSError as e:
            self.optimization_suggestions.append(
                f"Cannot read image file: {image_path} - {e}"
            )
        
        return info
    
    def _get_image_dimensions(self, image_path: Path) -> Optional[Tuple[int, int]]:
        """Get image dimensions if possible."""
        try:
            # Try to use PIL if available
            try:
                from PIL import Image
                with Image.open(image_path) as img:
                    return img.size
            except ImportError:
                pass
            
            # Fallback: try to read basic image headers
            if image_path.suffix.lower() in ['.png']:
                return self._get_png_dimensions(image_path)
            elif image_path.suffix.lower() in ['.jpg', '.jpeg']:
                return self._get_jpeg_dimensions(image_path)
            
        except Exception:
            pass
        
        return None
    
    def _get_png_dimensions(self, image_path: Path) -> Optional[Tuple[int, int]]:
        """Get PNG dimensions from header."""
        try:
            with open(image_path, 'rb') as f:
                # PNG signature
                if f.read(8) != b'\x89PNG\r\n\x1a\n':
                    return None
                
                # IHDR chunk
                f.read(4)  # chunk length
                if f.read(4) != b'IHDR':
                    return None
                
                # Width and height (4 bytes each, big-endian)
                width = int.from_bytes(f.read(4), 'big')
                height = int.from_bytes(f.read(4), 'big')
                
                return (width, height)
        except Exception:
            return None
    
    def _get_jpeg_dimensions(self, image_path: Path) -> Optional[Tuple[int, int]]:
        """Get JPEG dimensions from header (simplified)."""
        try:
            with open(image_path, 'rb') as f:
                # JPEG signature
                if f.read(2) != b'\xff\xd8':
                    return None
                
                # This is a simplified implementation
                # A full JPEG parser would be more complex
                return None
        except Exception:
            return None
    
    def _suggest_format_optimization(self, image_path: Path, info: ImageInfo):
        """Suggest format optimizations."""
        suffix = image_path.suffix.lower()
        
        # Suggest WebP for large images
        if info.file_size and info.file_size > self.WARNING_IMAGE_SIZE:
            if suffix in ['.jpg', '.jpeg', '.png']:
                self.optimization_suggestions.append(
                    f"Consider converting to WebP format: {image_path} "
                    f"- can reduce file size by 25-50%"
                )
        
        # Suggest SVG for simple graphics
        if suffix == '.png' and info.dimensions:
            width, height = info.dimensions
            if width < 500 and height < 500:
                self.optimization_suggestions.append(
                    f"Consider SVG format for small graphics: {image_path} "
                    f"- scalable and often smaller file size"
                )
        
        # Suggest JPEG for photos
        if suffix == '.png' and info.file_size and info.file_size > self.OPTIMAL_IMAGE_SIZE:
            self.optimization_suggestions.append(
                f"Consider JPEG format for photos: {image_path} "
                f"- better compression for photographic content"
            )
    
    def generate_optimization_report(self, result: ImageValidationResult) -> str:
        """Generate a human-readable optimization report."""
        report_lines = [
            "# Image Optimization Report",
            "",
            f"**Total Images:** {result.total_images}",
            f"**Valid Images:** {result.valid_images}",
            f"**Missing Images:** {result.missing_images}",
            f"**Oversized Images:** {result.oversized_images}",
            f"**Images Without Alt Text:** {result.images_without_alt}",
            f"**Success Rate:** {result.success_rate:.1f}%",
            ""
        ]
        
        if result.optimization_suggestions:
            report_lines.extend([
                "## Optimization Suggestions",
                ""
            ])
            for i, suggestion in enumerate(result.optimization_suggestions, 1):
                report_lines.append(f"{i}. {suggestion}")
            report_lines.append("")
        
        if result.missing_images > 0:
            report_lines.extend([
                "## Missing Images",
                ""
            ])
            for info in result.image_info:
                if not info.exists:
                    report_lines.append(f"- {info.path}")
            report_lines.append("")
        
        if result.oversized_images > 0:
            report_lines.extend([
                "## Large Images",
                ""
            ])
            for info in result.image_info:
                if info.file_size and info.file_size > self.WARNING_IMAGE_SIZE:
                    size_mb = info.file_size / 1024 / 1024
                    report_lines.append(f"- {info.path} ({size_mb:.1f}MB)")
            report_lines.append("")
        
        return "\n".join(report_lines)