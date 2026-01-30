"""
Base API Client with comprehensive error handling, retry logic, and logging.

This module provides a robust foundation for all external API integrations with:
- Exponential backoff retry mechanism
- Error categorization and mapping
- Request/response logging (with API key masking)
- Rate limit handling with automatic backoff
- Webhook and polling support
- Timeout management
"""

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional, Callable, TypeVar, Generic
from pathlib import Path

import httpx
from app.core.logger import logger
from app.core.config import settings


class APIErrorCategory(Enum):
    """Categorization of API errors for handling strategies"""
    AUTH_ERROR = "auth_error"           # 401 - Invalid API key, need re-auth
    FORBIDDEN = "forbidden"             # 403 - Access denied, no retry
    RATE_LIMITED = "rate_limited"       # 429 - Need backoff
    CLIENT_ERROR = "client_error"       # 4xx - Bad request, no retry
    SERVER_ERROR = "server_error"       # 500 - Retry with backoff
    BAD_GATEWAY = "bad_gateway"         # 502 - Retry
    UNAVAILABLE = "unavailable"         # 503 - Fallback to backup
    TIMEOUT = "timeout"                 # Request timeout - Retry
    NETWORK_ERROR = "network_error"     # Connection error - Retry
    UNKNOWN = "unknown"                 # Unknown error


@dataclass
class APIError(Exception):
    """Structured API error with categorization"""
    category: APIErrorCategory
    status_code: Optional[int]
    message: str
    original_error: Optional[Exception] = None
    retry_after: Optional[int] = None  # Seconds to wait before retry
    request_id: Optional[str] = None
    api_name: str = "unknown"
    
    def __str__(self) -> str:
        return f"[{self.api_name}] {self.category.value}: {self.message} (HTTP {self.status_code})"
    
    def is_retryable(self) -> bool:
        """Check if this error should trigger a retry"""
        return self.category in [
            APIErrorCategory.RATE_LIMITED,
            APIErrorCategory.SERVER_ERROR,
            APIErrorCategory.BAD_GATEWAY,
            APIErrorCategory.TIMEOUT,
            APIErrorCategory.NETWORK_ERROR,
        ]


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True  # Add randomness to prevent thundering herd
    
    def get_delay(self, attempt: int, retry_after: Optional[int] = None) -> float:
        """Calculate delay for a specific retry attempt"""
        if retry_after:
            return min(float(retry_after), self.max_delay)
        
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            import random
            delay = delay * (0.5 + random.random())
        
        return delay


@dataclass  
class RequestLog:
    """Log entry for API requests"""
    request_id: str
    api_name: str
    method: str
    url: str
    timestamp: datetime
    duration_ms: Optional[float] = None
    status_code: Optional[int] = None
    success: bool = False
    error_message: Optional[str] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "request_id": self.request_id,
            "api_name": self.api_name,
            "method": self.method,
            "url": self._mask_url(self.url),
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "status_code": self.status_code,
            "success": self.success,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
        }
    
    def _mask_url(self, url: str) -> str:
        """Mask sensitive parameters in URL"""
        import re
        # Mask API keys in query params
        masked = re.sub(r'(api_key|key|token|secret)=[^&]+', r'\1=***MASKED***', url, flags=re.IGNORECASE)
        return masked


@dataclass
class PipelineStep:
    """Represents a step in the video processing pipeline"""
    name: str
    status: str = "pending"  # pending, running, completed, failed
    progress: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def duration_ms(self) -> Optional[float]:
        """Get step duration in milliseconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None


class BaseAPIClient(ABC):
    """
    Base class for all external API clients.
    
    Provides:
    - HTTP client with retry logic
    - Error categorization and handling
    - Request/response logging
    - Rate limit management
    """
    
    api_name: str = "base"
    base_url: str = ""
    
    # Error code mapping - override in subclasses for API-specific handling
    ERROR_CODE_MAPPING: Dict[int, APIErrorCategory] = {
        400: APIErrorCategory.CLIENT_ERROR,
        401: APIErrorCategory.AUTH_ERROR,
        403: APIErrorCategory.FORBIDDEN,
        404: APIErrorCategory.CLIENT_ERROR,
        422: APIErrorCategory.CLIENT_ERROR,
        429: APIErrorCategory.RATE_LIMITED,
        500: APIErrorCategory.SERVER_ERROR,
        502: APIErrorCategory.BAD_GATEWAY,
        503: APIErrorCategory.UNAVAILABLE,
        504: APIErrorCategory.TIMEOUT,
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        retry_config: Optional[RetryConfig] = None,
    ):
        self.api_key = api_key
        self.timeout = timeout
        self.retry_config = retry_config or RetryConfig()
        self._client: Optional[httpx.AsyncClient] = None
        self._request_logs: list[RequestLog] = []
        
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers=self._get_default_headers(),
            )
        return self._client
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for requests - override in subclasses"""
        headers = {
            "User-Agent": f"VideoTool/{settings.APP_VERSION}",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def _categorize_error(self, status_code: int) -> APIErrorCategory:
        """Categorize HTTP error code"""
        return self.ERROR_CODE_MAPPING.get(status_code, APIErrorCategory.UNKNOWN)
    
    async def _make_request(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        """
        Make an HTTP request with retry logic and error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            url: Request URL
            **kwargs: Additional arguments for httpx request
            
        Returns:
            httpx.Response object
            
        Raises:
            APIError: On request failure after retries
        """
        request_id = str(uuid.uuid4())[:8]
        start_time = datetime.now(timezone.utc)
        
        log_entry = RequestLog(
            request_id=request_id,
            api_name=self.api_name,
            method=method.upper(),
            url=url,
            timestamp=start_time,
        )
        
        last_error: Optional[APIError] = None
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                log_entry.retry_count = attempt
                
                logger.info(
                    f"[{self.api_name}] {method.upper()} {log_entry._mask_url(url)} "
                    f"(attempt {attempt + 1}/{self.retry_config.max_retries + 1})"
                )
                
                client = await self._get_client()
                response = await client.request(method, url, **kwargs)
                
                # Calculate duration
                duration = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                log_entry.duration_ms = duration
                log_entry.status_code = response.status_code
                
                # Check for error status codes
                if response.status_code >= 400:
                    error_category = self._categorize_error(response.status_code)
                    retry_after = response.headers.get("Retry-After")
                    
                    error = APIError(
                        category=error_category,
                        status_code=response.status_code,
                        message=self._extract_error_message(response),
                        retry_after=int(retry_after) if retry_after else None,
                        request_id=request_id,
                        api_name=self.api_name,
                    )
                    
                    if error.is_retryable() and attempt < self.retry_config.max_retries:
                        delay = self.retry_config.get_delay(attempt, error.retry_after)
                        logger.warning(
                            f"[{self.api_name}] Retryable error: {error}. "
                            f"Waiting {delay:.2f}s before retry..."
                        )
                        await asyncio.sleep(delay)
                        last_error = error
                        continue
                    
                    log_entry.success = False
                    log_entry.error_message = str(error)
                    self._request_logs.append(log_entry)
                    logger.error(f"[{self.api_name}] Request failed: {log_entry.to_dict()}")
                    raise error
                
                # Success
                log_entry.success = True
                self._request_logs.append(log_entry)
                logger.info(
                    f"[{self.api_name}] Request successful: "
                    f"{response.status_code} in {duration:.0f}ms"
                )
                return response
                
            except httpx.TimeoutException as e:
                error = APIError(
                    category=APIErrorCategory.TIMEOUT,
                    status_code=None,
                    message=f"Request timed out after {self.timeout}s",
                    original_error=e,
                    request_id=request_id,
                    api_name=self.api_name,
                )
                
                if attempt < self.retry_config.max_retries:
                    delay = self.retry_config.get_delay(attempt)
                    logger.warning(f"[{self.api_name}] Timeout. Retrying in {delay:.2f}s...")
                    await asyncio.sleep(delay)
                    last_error = error
                    continue
                    
                log_entry.success = False
                log_entry.error_message = str(error)
                self._request_logs.append(log_entry)
                raise error
                
            except httpx.ConnectError as e:
                error = APIError(
                    category=APIErrorCategory.NETWORK_ERROR,
                    status_code=None,
                    message=f"Connection error: {str(e)}",
                    original_error=e,
                    request_id=request_id,
                    api_name=self.api_name,
                )
                
                if attempt < self.retry_config.max_retries:
                    delay = self.retry_config.get_delay(attempt)
                    logger.warning(f"[{self.api_name}] Connection error. Retrying in {delay:.2f}s...")
                    await asyncio.sleep(delay)
                    last_error = error
                    continue
                    
                log_entry.success = False
                log_entry.error_message = str(error)
                self._request_logs.append(log_entry)
                raise error
        
        # Should not reach here, but just in case
        if last_error:
            raise last_error
        raise APIError(
            category=APIErrorCategory.UNKNOWN,
            status_code=None,
            message="Unknown error after retries",
            request_id=request_id,
            api_name=self.api_name,
        )
    
    def _extract_error_message(self, response: httpx.Response) -> str:
        """Extract error message from response - override in subclasses"""
        try:
            data = response.json()
            # Common error message fields
            for field in ["error", "message", "detail", "error_message"]:
                if field in data:
                    msg = data[field]
                    if isinstance(msg, dict):
                        return str(msg.get("message", msg))
                    return str(msg)
            return str(data)
        except Exception:
            return response.text[:200] if response.text else f"HTTP {response.status_code}"
    
    async def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make a GET request"""
        url = f"{self.base_url}{endpoint}"
        response = await self._make_request("GET", url, params=params, **kwargs)
        return response.json()
    
    async def post(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make a POST request"""
        url = f"{self.base_url}{endpoint}"
        response = await self._make_request("POST", url, data=data, json=json, **kwargs)
        return response.json()
    
    async def put(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make a PUT request"""
        url = f"{self.base_url}{endpoint}"
        response = await self._make_request("PUT", url, data=data, json=json, **kwargs)
        return response.json()
    
    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a DELETE request"""
        url = f"{self.base_url}{endpoint}"
        response = await self._make_request("DELETE", url, **kwargs)
        return response.json()
    
    def get_request_logs(self) -> list[RequestLog]:
        """Get all request logs for debugging"""
        return self._request_logs
    
    def clear_request_logs(self):
        """Clear request logs"""
        self._request_logs.clear()
    
    async def close(self):
        """Close the HTTP client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    # Abstract methods for subclasses
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the API is available"""
        pass


class WebhookHandler:
    """
    Handle webhook callbacks from external APIs.
    
    Provides:
    - Webhook endpoint registration
    - Status update callbacks
    - Retry mechanism for failed webhooks
    """
    
    def __init__(self, callback_url: Optional[str] = None):
        self.callback_url = callback_url
        self._handlers: Dict[str, Callable] = {}
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register a handler for a specific event type"""
        self._handlers[event_type] = handler
    
    async def handle_webhook(self, event_type: str, payload: Dict[str, Any]):
        """Process incoming webhook"""
        handler = self._handlers.get(event_type)
        if handler:
            await handler(payload)
        else:
            logger.warning(f"No handler registered for webhook event: {event_type}")


class PollingClient:
    """
    Poll for job status updates when webhooks are not available.
    
    Features:
    - Exponential backoff polling
    - Maximum poll attempts
    - Status change callbacks
    """
    
    def __init__(
        self,
        poll_interval: float = 5.0,
        max_polls: int = 120,  # 10 minutes at 5s interval
        backoff_multiplier: float = 1.5,
        max_interval: float = 30.0,
    ):
        self.poll_interval = poll_interval
        self.max_polls = max_polls
        self.backoff_multiplier = backoff_multiplier
        self.max_interval = max_interval
    
    async def poll_until_complete(
        self,
        check_status: Callable[[], Any],
        is_complete: Callable[[Any], bool],
        is_failed: Callable[[Any], bool],
        on_progress: Optional[Callable[[Any], None]] = None,
    ) -> Any:
        """
        Poll until job is complete or failed.
        
        Args:
            check_status: Async function that returns current status
            is_complete: Function to check if status indicates completion
            is_failed: Function to check if status indicates failure
            on_progress: Optional callback for progress updates
            
        Returns:
            Final status object
            
        Raises:
            APIError: On failure or timeout
        """
        current_interval = self.poll_interval
        
        for attempt in range(self.max_polls):
            status = await check_status()
            
            if on_progress:
                on_progress(status)
            
            if is_complete(status):
                logger.info(f"Polling complete after {attempt + 1} attempts")
                return status
            
            if is_failed(status):
                raise APIError(
                    category=APIErrorCategory.SERVER_ERROR,
                    status_code=None,
                    message=f"Job failed: {status}",
                    api_name="polling",
                )
            
            logger.debug(f"Polling attempt {attempt + 1}/{self.max_polls}, waiting {current_interval:.1f}s")
            await asyncio.sleep(current_interval)
            
            # Increase interval with backoff
            current_interval = min(current_interval * self.backoff_multiplier, self.max_interval)
        
        raise APIError(
            category=APIErrorCategory.TIMEOUT,
            status_code=None,
            message=f"Polling timed out after {self.max_polls} attempts",
            api_name="polling",
        )
