"""
Simple live server with auto-reload functionality for development mode.

Provides a lightweight HTTP server with WebSocket-based auto-reload
for seamless development experience when working with generated slides.
"""

import asyncio
import json
import webbrowser
from pathlib import Path
from typing import Set, Optional, Callable, Awaitable
import logging
import socket

from aiohttp import web, WSMsgType
from aiohttp.web_ws import WebSocketResponse

from .logger import get_logger


logger = get_logger(__name__)


class LiveServer:
    """
    Simple HTTP server with WebSocket-based auto-reload functionality.
    
    Serves static files and provides real-time browser refresh capability
    for development workflows.
    """
    
    def __init__(self, serve_dir: Path, port: int = 8000):
        """
        Initialize the live server.
        
        Args:
            serve_dir: Directory to serve files from
            port: Port number for the server
        """
        self.serve_dir = serve_dir.resolve()
        self.port = port
        self.app = web.Application()
        self.websockets: Set[WebSocketResponse] = set()
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """Setup HTTP and WebSocket routes."""
        # WebSocket endpoint for live reload
        self.app.router.add_get('/ws', self._websocket_handler)
        
        # Static file serving with auto-reload injection
        self.app.router.add_get('/{path:.*}', self._static_handler)
    
    async def _websocket_handler(self, request: web.Request) -> WebSocketResponse:
        """Handle WebSocket connections for live reload."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websockets.add(ws)
        logger.debug(f"WebSocket connected. Active connections: {len(self.websockets)}")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")
                    break
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.websockets.discard(ws)
            logger.debug(f"WebSocket disconnected. Active connections: {len(self.websockets)}")
        
        return ws
    
    async def _static_handler(self, request: web.Request) -> web.StreamResponse:
        """Serve static files with auto-reload script injection for HTML files."""
        path = request.match_info.get('path', 'index.html')
        
        # Handle root path - redirect to slides file if available
        if not path or path == 'index.html' or path.endswith('/'):
            # Look for slides files first
            html_files = list(self.serve_dir.glob("*.html"))
            slide_files = [f for f in html_files if "_slides.html" in f.name]
            
            if slide_files:
                # Redirect to the slides file
                redirect_path = f"/{slide_files[0].name}"
                logger.debug(f"Redirecting root to: {redirect_path}")
                return web.Response(
                    status=302,
                    headers={'Location': redirect_path}
                )
            elif html_files:
                # Redirect to any HTML file
                redirect_path = f"/{html_files[0].name}"
                logger.debug(f"Redirecting root to: {redirect_path}")
                return web.Response(
                    status=302,
                    headers={'Location': redirect_path}
                )
            else:
                path = 'index.html'  # fallback
        
        file_path = self.serve_dir / path
        logger.debug(f"Requested path: '{path}' -> file_path: {file_path}")
        
        # Try to find HTML files if exact path doesn't exist
        if not file_path.exists():
            # Look for slide files in the directory
            html_files = list(self.serve_dir.glob("*.html"))
            logger.debug(f"Found HTML files: {[f.name for f in html_files]}")
            
            # Prioritize slides files
            slide_files = [f for f in html_files if "_slides.html" in f.name]
            if slide_files:
                logger.debug(f"Using slides file: {slide_files[0].name}")
                file_path = slide_files[0]  # Use the first slides file found
            elif html_files:
                logger.debug(f"Using fallback HTML file: {html_files[0].name}")
                file_path = html_files[0]  # Use any HTML file as fallback
            else:
                # Still try the old logic as final fallback
                possible_names = [
                    f"{self.serve_dir.name}_slides.html",
                    "slides.html", 
                    "index.html"
                ]
                
                for name in possible_names:
                    candidate = self.serve_dir / name
                    if candidate.exists():
                        file_path = candidate
                        break
        
        if not file_path.exists() or not file_path.is_file():
            return web.Response(text="File not found", status=404)
        
        try:
            # Handle HTML files with auto-reload script injection
            if file_path.suffix.lower() == '.html':
                content = file_path.read_text(encoding='utf-8')
                content = self._inject_reload_script(content)
                return web.Response(text=content, content_type='text/html')
            else:
                # Serve binary and other files directly using FileResponse
                return web.FileResponse(file_path)
                
        except Exception as e:
            logger.error(f"Error serving file {file_path}: {e}")
            return web.Response(text="Error reading file", status=500)
    
    def _inject_reload_script(self, html_content: str) -> str:
        """Inject auto-reload WebSocket script into HTML content."""
        reload_script = '''
<script>
(function() {
    // Auto-reload functionality
    const ws = new WebSocket(`ws://${location.host}/ws`);
    
    ws.onopen = function() {
        console.log('🔄 Live reload connected');
    };
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'reload') {
            console.log('🔄 Reloading page...');
            window.location.reload();
        }
    };
    
    ws.onclose = function() {
        console.log('🔄 Live reload disconnected - attempting reconnect in 1s...');
        setTimeout(() => window.location.reload(), 1000);
    };
    
    ws.onerror = function() {
        console.log('🔄 Live reload error - will retry on page reload');
    };
})();
</script>
'''
        
        # Try to inject before </body>, fallback to </html>, or append at end
        if '</body>' in html_content:
            return html_content.replace('</body>', reload_script + '\n</body>')
        elif '</html>' in html_content:
            return html_content.replace('</html>', reload_script + '\n</html>')
        else:
            return html_content + reload_script
    
    async def broadcast_reload(self) -> None:
        """Broadcast reload message to all connected WebSocket clients."""
        if not self.websockets:
            logger.debug("No WebSocket connections to notify")
            return
        
        message = json.dumps({'type': 'reload'})
        disconnected = set()
        
        for ws in self.websockets:
            try:
                await ws.send_str(message)
                logger.debug("Sent reload message to client")
            except Exception as e:
                logger.debug(f"Failed to send reload message: {e}")
                disconnected.add(ws)
        
        # Remove disconnected websockets
        self.websockets -= disconnected
    
    def _find_free_port(self, start_port: int) -> int:
        """Find a free port starting from the given port."""
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        raise RuntimeError(f"Could not find a free port starting from {start_port}")
    
    async def start(self) -> str:
        """
        Start the server.
        
        Returns:
            The server URL
        """
        # Find a free port if the requested one is taken
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', self.port))
        except OSError:
            original_port = self.port
            self.port = self._find_free_port(self.port)
            logger.info(f"Port {original_port} was busy, using port {self.port} instead")
        
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        
        self.site = web.TCPSite(self.runner, 'localhost', self.port)
        await self.site.start()
        
        server_url = f"http://localhost:{self.port}"
        logger.info(f"Live server started at {server_url}")
        return server_url
    
    async def stop(self) -> None:
        """Stop the server."""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("Live server stopped")


async def start_live_server(
    serve_dir: Path, 
    port: int = 8000,
    auto_open: bool = True,
    target_file: Optional[str] = None
) -> LiveServer:
    """
    Start a live server and optionally open the browser.
    
    Args:
        serve_dir: Directory to serve files from
        port: Port number for the server
        auto_open: Whether to automatically open the browser
        target_file: Specific file to open (optional)
        
    Returns:
        LiveServer instance
    """
    server = LiveServer(serve_dir, port)
    server_url = await server.start()
    
    if auto_open:
        # Construct URL with target file if specified
        if target_file:
            target_url = f"{server_url}/{target_file}"
            logger.info(f"Opening browser to {target_file}...")
            webbrowser.open(target_url)
        else:
            logger.info("Opening browser...")
            webbrowser.open(server_url)
    
    return server
