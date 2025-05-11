from locust import HttpUser, task, between
from loguru import logger
from typing import Dict, Any, Optional
import json

class BaseLocustUser(HttpUser):
    """Base class for all Locust user behaviors"""
    
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
    
    def make_request(self, method: str, path: str, 
                    expected_status: int = 200,
                    json_data: Optional[Dict[str, Any]] = None,
                    name: Optional[str] = None) -> Dict[str, Any]:
        """
        Make an HTTP request with proper logging and error handling
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            expected_status: Expected HTTP status code
            json_data: Optional JSON data for request body
            name: Optional name for the request (for Locust statistics)
            
        Returns:
            Response data as dictionary
        """
        request_name = name or f"{method} {path}"
        
        with self.client.request(method, path, 
                               json=json_data,
                               catch_response=True,
                               name=request_name) as response:
            if response.status_code == expected_status:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    self.logger.warning(f"Response is not JSON: {response.text}")
                    return {"raw_response": response.text}
            else:
                self.logger.error(f"Request failed: {response.status_code} - {response.text}")
                response.failure(f"Expected status {expected_status}, got {response.status_code}")
                return {} 