"""
Autonomous Context Logging Middleware for Trinity Context Core.

Automatically captures and logs API interactions to memory without blocking requests.
"""
import json
from typing import Callable
from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.background import BackgroundTask

from ..core.logger import ContextLogger


class ContextLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that automatically logs API interactions to memory.
    
    Features:
    - Non-blocking background logging
    - Filters out errors and empty requests
    - Captures request-response pairs
    - Automatic importance boosting for key topics
    """
    
    # Paths to monitor for automatic logging
    MONITORED_PATHS = [
        "/api/v1/memory/search",
        "/api/v1/memory/add"
    ]
    
    def __init__(self, app, logger: ContextLogger = None):
        """
        Initialize the middleware.
        
        Args:
            app: FastAPI application instance
            logger: Optional ContextLogger instance
        """
        super().__init__(app)
        self.logger = logger or ContextLogger()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process each request and log interactions in the background.
        
        Args:
            request: The incoming request
            call_next: The next middleware/endpoint to call
            
        Returns:
            The response from the endpoint
        """
        # Check if this path should be logged
        should_log = any(
            request.url.path.startswith(path) 
            for path in self.MONITORED_PATHS
        )
        
        if not should_log:
            # Pass through without logging
            return await call_next(request)
        
        # Capture request body (but preserve it for the endpoint)
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body_bytes = await request.body()
            # Store body for logging
            request_body = self._parse_body(body_bytes)
            
            # Create a new receive callable that returns the cached body
            async def receive():
                return {"type": "http.request", "body": body_bytes}
            
            # Replace the request's receive with our cached version
            request._receive = receive
        
        # Process the request
        response = await call_next(request)
        
        # Only log successful requests (2xx status codes)
        if 200 <= response.status_code < 300 and request_body:
            # Schedule background logging (non-blocking)
            background_task = BackgroundTask(
                self._log_interaction,
                path=request.url.path,
                method=request.method,
                request_body=request_body,
                status_code=response.status_code
            )
            
            # Attach background task to response
            if hasattr(response, 'background'):
                response.background = background_task
        
        return response
    
    def _parse_body(self, body_bytes: bytes) -> dict:
        """
        Parse request body from bytes.
        
        Args:
            body_bytes: Raw body bytes
            
        Returns:
            Parsed request body as dict
        """
        try:
            if body_bytes:
                return json.loads(body_bytes.decode('utf-8'))
            return {}
        except Exception as e:
            print(f"[Middleware] Could not parse request body: {e}")
            return {}
    
    def _log_interaction(
        self, 
        path: str, 
        method: str, 
        request_body: dict,
        status_code: int
    ):
        """
        Log the API interaction to memory (runs in background).
        
        Args:
            path: API endpoint path
            method: HTTP method
            request_body: Request body data
            status_code: Response status code
        """
        try:
            # Skip empty requests
            if not request_body:
                return
            
            # Build interaction description
            interaction_parts = []
            
            if "/search" in path:
                query = request_body.get("query", "")
                if query:
                    interaction_parts.append(f"Search query: {query}")
            
            elif "/add" in path:
                content = request_body.get("content", "")
                tags = request_body.get("tags", [])
                if content:
                    interaction_parts.append(f"Added memory: {content[:100]}")
                    if tags:
                        interaction_parts.append(f"Tags: {', '.join(tags)}")
            
            if not interaction_parts:
                return
            
            # Create log content
            log_content = " | ".join(interaction_parts)
            
            # Determine tags based on endpoint
            log_tags = ["api_interaction"]
            if "/search" in path:
                log_tags.append("search")
            elif "/add" in path:
                log_tags.append("memory_add")
            
            # Log to memory with automatic importance boosting
            self.logger.commit_to_memory(
                content=log_content,
                tags=log_tags,
                importance=5  # Will be boosted if keywords present
            )
            
        except Exception as e:
            # Fail silently - logging errors shouldn't break the API
            print(f"[Middleware] Background logging error: {e}")


class ContextCapturingRoute(APIRoute):
    """
    Custom route class for capturing request/response bodies.
    
    This is an alternative approach using custom route handlers
    instead of middleware. Can be used for more granular control.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = ContextLogger()
    
    def get_route_handler(self) -> Callable:
        """Get the route handler with logging."""
        original_handler = super().get_route_handler()
        
        async def logging_handler(request: Request) -> Response:
            # Get original response
            response = await original_handler(request)
            
            # Log in background if needed
            # (implementation would be similar to middleware)
            
            return response
        
        return logging_handler
