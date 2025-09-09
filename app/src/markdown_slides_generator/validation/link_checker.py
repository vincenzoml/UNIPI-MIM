"""
Link Checker - Validates links and references in academic content.

Checks for broken links, validates academic references, and ensures
proper link formatting for different output formats.
"""

import re
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse, urljoin
import time

from ..utils.logger import get_logger
from ..utils.exceptions import handle_exception

logger = get_logger(__name__)


@dataclass
class LinkValidationResult:
    """Result of link validation."""
    url: str
    is_valid: bool
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    response_time: Optional[float] = None
    redirect_url: Optional[str] = None


@dataclass
class LinkCheckResult:
    """Overall result of link checking."""
    total_links: int
    valid_links: int
    broken_links: int
    warnings: int
    results: List[LinkValidationResult]
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_links == 0:
            return 100.0
        return (self.valid_links / self.total_links) * 100.0


class LinkChecker:
    """
    Comprehensive link validation system for academic content.
    
    Validates HTTP/HTTPS links, checks local file references,
    and ensures proper academic citation formatting.
    """
    
    # Link patterns
    MARKDOWN_LINK_PATTERN = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
    HTML_LINK_PATTERN = re.compile(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>')
    REFERENCE_LINK_PATTERN = re.compile(r'\[([^\]]+)\]:\s*(.+)')
    
    # Academic reference patterns
    DOI_PATTERN = re.compile(r'10\.\d{4,}/[^\s]+')
    ARXIV_PATTERN = re.compile(r'arxiv:\d{4}\.\d{4,5}', re.IGNORECASE)
    
    # URL validation
    VALID_SCHEMES = {'http', 'https', 'ftp', 'mailto', 'file'}
    
    def __init__(self, timeout: int = 10, max_concurrent: int = 10):
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.session: Optional[aiohttp.ClientSession] = None
    
    @handle_exception
    async def check_links(self, content: str, base_path: Optional[Path] = None) -> LinkCheckResult:
        """
        Check all links in the given content.
        
        Args:
            content: Markdown content to check
            base_path: Base path for resolving relative links
            
        Returns:
            LinkCheckResult with validation results
        """
        logger.info("Starting comprehensive link validation")
        
        # Extract all links from content
        links = self._extract_links(content)
        logger.info(f"Found {len(links)} links to validate")
        
        if not links:
            return LinkCheckResult(
                total_links=0,
                valid_links=0,
                broken_links=0,
                warnings=0,
                results=[]
            )
        
        # Validate links
        results = await self._validate_links(links, base_path)
        
        # Analyze results
        valid_count = sum(1 for r in results if r.is_valid)
        broken_count = sum(1 for r in results if not r.is_valid)
        warning_count = sum(1 for r in results if r.status_code and 300 <= r.status_code < 400)
        
        result = LinkCheckResult(
            total_links=len(results),
            valid_links=valid_count,
            broken_links=broken_count,
            warnings=warning_count,
            results=results
        )
        
        logger.info(f"Link validation complete: {valid_count} valid, {broken_count} broken, "
                   f"{warning_count} warnings ({result.success_rate:.1f}% success rate)")
        
        return result
    
    def _extract_links(self, content: str) -> List[Tuple[str, str]]:
        """
        Extract all links from markdown content.
        
        Returns:
            List of (link_text, url) tuples
        """
        links = []
        
        # Extract markdown links
        markdown_links = self.MARKDOWN_LINK_PATTERN.findall(content)
        links.extend(markdown_links)
        
        # Extract HTML links
        html_links = self.HTML_LINK_PATTERN.findall(content)
        links.extend([('', url) for url in html_links])
        
        # Extract reference-style links
        reference_links = self.REFERENCE_LINK_PATTERN.findall(content)
        links.extend(reference_links)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for text, url in links:
            if url not in seen:
                seen.add(url)
                unique_links.append((text, url))
        
        return unique_links
    
    async def _validate_links(self, links: List[Tuple[str, str]], base_path: Optional[Path]) -> List[LinkValidationResult]:
        """Validate a list of links."""
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Create HTTP session
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            self.session = session
            
            # Create validation tasks
            tasks = [
                self._validate_single_link(semaphore, text, url, base_path)
                for text, url in links
            ]
            
            # Execute all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            validated_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    _, url = links[i]
                    validated_results.append(LinkValidationResult(
                        url=url,
                        is_valid=False,
                        error_message=str(result)
                    ))
                else:
                    validated_results.append(result)
            
            return validated_results
    
    async def _validate_single_link(self, semaphore: asyncio.Semaphore, text: str, url: str, base_path: Optional[Path]) -> LinkValidationResult:
        """Validate a single link."""
        async with semaphore:
            start_time = time.time()
            
            try:
                # Handle different URL types
                parsed_url = urlparse(url)
                
                if parsed_url.scheme in ('http', 'https'):
                    result = await self._validate_http_link(url)
                elif parsed_url.scheme == 'mailto':
                    result = self._validate_mailto_link(url)
                elif parsed_url.scheme == 'file' or not parsed_url.scheme:
                    result = self._validate_file_link(url, base_path)
                elif parsed_url.scheme == 'ftp':
                    result = self._validate_ftp_link(url)
                else:
                    result = LinkValidationResult(
                        url=url,
                        is_valid=False,
                        error_message=f"Unsupported URL scheme: {parsed_url.scheme}"
                    )
                
                result.response_time = time.time() - start_time
                return result
                
            except Exception as e:
                return LinkValidationResult(
                    url=url,
                    is_valid=False,
                    error_message=str(e),
                    response_time=time.time() - start_time
                )
    
    async def _validate_http_link(self, url: str) -> LinkValidationResult:
        """Validate HTTP/HTTPS link."""
        try:
            async with self.session.get(url, allow_redirects=True) as response:
                is_valid = response.status < 400
                redirect_url = str(response.url) if str(response.url) != url else None
                
                return LinkValidationResult(
                    url=url,
                    is_valid=is_valid,
                    status_code=response.status,
                    redirect_url=redirect_url
                )
                
        except aiohttp.ClientError as e:
            return LinkValidationResult(
                url=url,
                is_valid=False,
                error_message=f"HTTP error: {e}"
            )
        except asyncio.TimeoutError:
            return LinkValidationResult(
                url=url,
                is_valid=False,
                error_message="Request timeout"
            )
    
    def _validate_mailto_link(self, url: str) -> LinkValidationResult:
        """Validate mailto link."""
        # Basic email format validation
        email_pattern = re.compile(r'^mailto:[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        is_valid = bool(email_pattern.match(url))
        
        return LinkValidationResult(
            url=url,
            is_valid=is_valid,
            error_message="Invalid email format" if not is_valid else None
        )
    
    def _validate_file_link(self, url: str, base_path: Optional[Path]) -> LinkValidationResult:
        """Validate local file link."""
        try:
            # Handle relative paths
            if not url.startswith('/') and base_path:
                file_path = base_path / url
            else:
                file_path = Path(url)
            
            is_valid = file_path.exists()
            error_message = None if is_valid else f"File not found: {file_path}"
            
            return LinkValidationResult(
                url=url,
                is_valid=is_valid,
                error_message=error_message
            )
            
        except Exception as e:
            return LinkValidationResult(
                url=url,
                is_valid=False,
                error_message=f"File validation error: {e}"
            )
    
    def _validate_ftp_link(self, url: str) -> LinkValidationResult:
        """Validate FTP link (basic format check)."""
        # Basic FTP URL format validation
        ftp_pattern = re.compile(r'^ftp://[a-zA-Z0-9.-]+(/.*)?$')
        is_valid = bool(ftp_pattern.match(url))
        
        return LinkValidationResult(
            url=url,
            is_valid=is_valid,
            error_message="Invalid FTP URL format" if not is_valid else None
        )
    
    def check_academic_references(self, content: str) -> Dict[str, List[str]]:
        """
        Check for academic references and validate their format.
        
        Args:
            content: Content to check for academic references
            
        Returns:
            Dictionary with reference types and their occurrences
        """
        references = {
            'dois': [],
            'arxiv': [],
            'malformed_dois': [],
            'malformed_arxiv': []
        }
        
        # Find DOI references
        doi_matches = self.DOI_PATTERN.findall(content)
        for doi in doi_matches:
            if self._validate_doi_format(doi):
                references['dois'].append(doi)
            else:
                references['malformed_dois'].append(doi)
        
        # Find arXiv references
        arxiv_matches = self.ARXIV_PATTERN.findall(content)
        for arxiv in arxiv_matches:
            if self._validate_arxiv_format(arxiv):
                references['arxiv'].append(arxiv)
            else:
                references['malformed_arxiv'].append(arxiv)
        
        return references
    
    def _validate_doi_format(self, doi: str) -> bool:
        """Validate DOI format."""
        # DOI format: 10.xxxx/yyyy where xxxx is 4+ digits
        pattern = re.compile(r'^10\.\d{4,}/[^\s]+$')
        return bool(pattern.match(doi))
    
    def _validate_arxiv_format(self, arxiv: str) -> bool:
        """Validate arXiv format."""
        # arXiv format: arxiv:YYMM.NNNN or arxiv:YYMM.NNNNN
        pattern = re.compile(r'^arxiv:\d{4}\.\d{4,5}$', re.IGNORECASE)
        return bool(pattern.match(arxiv))
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()


# Synchronous wrapper for easier use
def check_links_sync(content: str, base_path: Optional[Path] = None, **kwargs) -> LinkCheckResult:
    """
    Synchronous wrapper for link checking.
    
    Args:
        content: Markdown content to check
        base_path: Base path for resolving relative links
        **kwargs: Additional arguments for LinkChecker
        
    Returns:
        LinkCheckResult with validation results
    """
    async def _check():
        checker = LinkChecker(**kwargs)
        return await checker.check_links(content, base_path)
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(_check())