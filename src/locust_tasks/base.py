from locust import HttpUser, task, between
from loguru import logger
from typing import Dict, Any, Optional, Callable, Union, List, Tuple
import json
from enum import Enum, auto
from urllib.parse import urlencode, urljoin
import time
from dataclasses import dataclass
from typing import TypeVar, Generic

T = TypeVar('T')

class HTTPMethod(Enum):
    """Enum for HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

@dataclass
class RetryConfig:
    """Configuration for request retries"""
    max_attempts: int = 3
    delay: float = 1.0
    backoff_factor: float = 2.0
    retry_on_status: List[int] = None

    def __post_init__(self):
        if self.retry_on_status is None:
            self.retry_on_status = [500, 502, 503, 504]

class ResponseValidator(Generic[T]):
    """Helper class for response validation"""
    
    def __init__(self, response: Any):
        self.response = response
        self._checks: List[Tuple[str, bool]] = []
    
    def status_is(self, status: int) -> 'ResponseValidator[T]':
        self._checks.append(("status", self.response.status_code == status))
        return self
    
    def has_header(self, header: str) -> 'ResponseValidator[T]':
        self._checks.append(("header", header in self.response.headers))
        return self
    
    def json_contains(self, key: str) -> 'ResponseValidator[T]':
        try:
            data = self.response.json()
            self._checks.append(("json_key", key in data))
        except json.JSONDecodeError:
            self._checks.append(("json_key", False))
        return self
    
    def json_matches(self, schema: Dict[str, Any]) -> 'ResponseValidator[T]':
        try:
            data = self.response.json()
            # Simple schema validation - can be enhanced with jsonschema
            for key, value in schema.items():
                if key not in data or data[key] != value:
                    self._checks.append(("json_schema", False))
                    return self
            self._checks.append(("json_schema", True))
        except json.JSONDecodeError:
            self._checks.append(("json_schema", False))
        return self
    
    def validate(self) -> bool:
        return all(check[1] for check in self._checks)

class RequestBuilder:
    """Builder class for constructing HTTP requests with a fluent API"""
    
    def __init__(self, user: 'BaseLocustUser', name: str):
        self.user = user
        self.name = name
        self.path = ""
        self.base_uri = user.base_uri
        self.method = HTTPMethod.GET
        self.headers: Dict[str, str] = {}
        self.json_data: Optional[Dict[str, Any]] = None
        self.form_data: Optional[Dict[str, Any]] = None
        self.files: Optional[Dict[str, Any]] = None
        self.query_params: Optional[Dict[str, Any]] = None
        self.expected_status = 200
        self.checks: list[Callable] = []
        self.timeout: Optional[float] = None
        self.retry_config: Optional[RetryConfig] = None
        self.log_request = True
        self.log_response = True
    
    def setRequestMethod(self, method: HTTPMethod) -> 'RequestBuilder':
        """Set the HTTP method for the request"""
        self.method = method
        return self
    
    def setBaseUri(self, uri: str) -> 'RequestBuilder':
        """Set the base URI for the request"""
        self.base_uri = uri
        return self
    
    def setBasePath(self, path: str) -> 'RequestBuilder':
        """Set the base path for the request"""
        self.path = path
        return self
    
    def addHeader(self, key: str, value: str) -> 'RequestBuilder':
        """Add a header to the request"""
        self.headers[key] = value
        return self
    
    def addHeaders(self, headers: Dict[str, str]) -> 'RequestBuilder':
        """Add multiple headers to the request"""
        self.headers.update(headers)
        return self
    
    def setJsonBody(self, data: Dict[str, Any]) -> 'RequestBuilder':
        """Set the JSON body for the request"""
        self.json_data = data
        return self
    
    def setFormData(self, data: Dict[str, Any]) -> 'RequestBuilder':
        """Set the form data for the request"""
        self.form_data = data
        return self
    
    def addFile(self, field_name: str, file_path: str, content_type: Optional[str] = None) -> 'RequestBuilder':
        """Add a file to the request"""
        if self.files is None:
            self.files = {}
        self.files[field_name] = (file_path, open(file_path, 'rb'), content_type)
        return self
    
    def addQueryParams(self, params: Dict[str, Any]) -> 'RequestBuilder':
        """Add query parameters to the request"""
        self.query_params = params
        return self
    
    def addQueryParam(self, key: str, value: Any) -> 'RequestBuilder':
        """Add a single query parameter to the request"""
        if self.query_params is None:
            self.query_params = {}
        self.query_params[key] = value
        return self
    
    def addCheck(self, check_func: Callable) -> 'RequestBuilder':
        """Add a check function to validate the response"""
        self.checks.append(check_func)
        return self
    
    def setExpectedStatus(self, status: int) -> 'RequestBuilder':
        """Set the expected HTTP status code"""
        self.expected_status = status
        return self
    
    def setTimeout(self, seconds: float) -> 'RequestBuilder':
        """Set the request timeout"""
        self.timeout = seconds
        return self
    
    def setRetryConfig(self, config: Optional[RetryConfig] = None) -> 'RequestBuilder':
        """Set the retry configuration"""
        self.retry_config = config or RetryConfig()
        return self
    
    def disableRequestLogging(self) -> 'RequestBuilder':
        """Disable request logging"""
        self.log_request = False
        return self
    
    def disableResponseLogging(self) -> 'RequestBuilder':
        """Disable response logging"""
        self.log_response = False
        return self
    
    def sendRequest(self) -> Dict[str, Any]:
        """Execute the request with all configured parameters"""
        # Combine base URI and path
        full_path = urljoin(self.base_uri, self.path)
        
        if self.query_params:
            query_string = urlencode(self.query_params)
            full_path = f"{full_path}?{query_string}"
        
        attempt = 0
        while True:
            try:
                response = self.user.make_request(
                    method=self.method,
                    path=full_path,
                    expected_status=self.expected_status,
                    json_data=self.json_data,
                    form_data=self.form_data,
                    files=self.files,
                    name=self.name,
                    headers=self.headers,
                    checks=self.checks,
                    timeout=self.timeout,
                    log_request=self.log_request,
                    log_response=self.log_response
                )
                
                if not self.retry_config:
                    return response
                
                attempt += 1
                if attempt >= self.retry_config.max_attempts:
                    return response
                
                if response.get('status_code') not in self.retry_config.retry_on_status:
                    return response
                
                delay = self.retry_config.delay * (self.retry_config.backoff_factor ** (attempt - 1))
                time.sleep(delay)
                
            except Exception as e:
                if not self.retry_config or attempt >= self.retry_config.max_attempts:
                    raise
                attempt += 1
                delay = self.retry_config.delay * (self.retry_config.backoff_factor ** (attempt - 1))
                time.sleep(delay)

class BaseLocustUser(HttpUser):
    """Base class for all Locust user behaviors"""
    
    # Default base URI - should be overridden by subclasses
    base_uri = "http://localhost:8080"
    
    wait_time = between(1, 3)  # Default wait time between tasks
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger.bind(user_type=self.__class__.__name__)
    
    def on_start(self):
        """Called when a user starts"""
        self.logger.info(f"User {self.__class__.__name__} started")
    
    def on_stop(self):
        """Called when a user stops"""
        self.logger.info(f"User {self.__class__.__name__} stopped")
    
    def http(self, name: str) -> RequestBuilder:
        """Start building a new HTTP request"""
        return RequestBuilder(self, name)
    
    def make_request(self, method: HTTPMethod, path: str, 
                    expected_status: int = 200,
                    json_data: Optional[Dict[str, Any]] = None,
                    form_data: Optional[Dict[str, Any]] = None,
                    files: Optional[Dict[str, Any]] = None,
                    name: Optional[str] = None,
                    headers: Optional[Dict[str, str]] = None,
                    checks: Optional[list[Callable]] = None,
                    timeout: Optional[float] = None,
                    log_request: bool = True,
                    log_response: bool = True) -> Dict[str, Any]:
        """
        Make an HTTP request with proper logging and error handling
        
        Args:
            method: HTTP method from HTTPMethod enum
            path: Request path
            expected_status: Expected HTTP status code
            json_data: Optional JSON data for request body
            form_data: Optional form data for request body
            files: Optional files to upload
            name: Optional name for the request (for Locust statistics)
            headers: Optional headers to include in the request
            checks: Optional list of check functions to run on the response
            timeout: Optional timeout in seconds
            log_request: Whether to log the request details
            log_response: Whether to log the response details
            
        Returns:
            Response data as dictionary
        """
        request_name = name or f"{method.value} {path}"
        headers = headers or {}
        
        if log_request:
            self.logger.debug(f"Making request: {method.value} {path}")
            if headers:
                self.logger.debug(f"Headers: {headers}")
            if json_data:
                self.logger.debug(f"JSON data: {json_data}")
            if form_data:
                self.logger.debug(f"Form data: {form_data}")
        
        with self.client.request(method.value, path, 
                               json=json_data,
                               data=form_data,
                               files=files,
                               headers=headers,
                               catch_response=True,
                               name=request_name,
                               timeout=timeout) as response:
            if response.status_code == expected_status:
                # Run any additional checks
                if checks:
                    for check in checks:
                        check(response)
                
                try:
                    result = response.json()
                    if log_response:
                        self.logger.debug(f"Response: {result}")
                    return result
                except json.JSONDecodeError:
                    self.logger.warning(f"Response is not JSON: {response.text}")
                    return {"raw_response": response.text}
            else:
                self.logger.error(f"Request failed: {response.status_code} - {response.text}")
                response.failure(f"Expected status {expected_status}, got {response.status_code}")
                return {} 