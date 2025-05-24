from locust import task, between
from typing import Dict, Any
from .base import BaseLocustUser, HTTPMethod, RetryConfig, ResponseValidator

class UserAPITest(BaseLocustUser):
    """
    Example class demonstrating the usage of all framework features.
    This class simulates a user interacting with a REST API.
    """
    
    # Override the default base URI
    base_uri = "https://api.example.com"
    
    # Override the default wait time
    wait_time = between(2, 5)
    
    def on_start(self):
        """Initialize test data when the user starts"""
        super().on_start()
        self.access_token = None
        self.user_id = None
    
    @task(1)
    def login_and_get_profile(self):
        """
        Example of a complete user flow with multiple requests and validations.
        Demonstrates:
        - Form data submission
        - Response validation
        - Header management
        - Retry mechanism
        - Error handling
        """
        # 1. Login with form data
        login_response = (self.http("User Login")
            .setRequestMethod(HTTPMethod.POST)
            .setBasePath("/auth/login")
            .setFormData({
                "username": "testuser",
                "password": "testpass"
            })
            .setExpectedStatus(200)
            .sendRequest())
        
        # Validate login response
        validator = ResponseValidator(login_response)
        if not validator.json_contains("access_token").validate():
            self.logger.error("Login failed - no access token in response")
            return
        
        self.access_token = login_response["access_token"]
        
        # 2. Get user profile with retry mechanism
        profile_response = (self.http("Get User Profile")
            .setRequestMethod(HTTPMethod.GET)
            .setBasePath("/users/profile")
            .addHeader("Authorization", f"Bearer {self.access_token}")
            .setRetryConfig(RetryConfig(
                max_attempts=3,
                delay=1.0,
                backoff_factor=2.0,
                retry_on_status=[500, 502, 503]
            ))
            .sendRequest())
        
        # Validate profile response
        profile_validator = ResponseValidator(profile_response)
        if not profile_validator.status_is(200).json_contains("id").validate():
            self.logger.error("Failed to get user profile")
            return
    
    @task(2)
    def create_and_update_user(self):
        """
        Example of creating and updating a user.
        Demonstrates:
        - JSON data submission
        - File upload
        - Query parameters
        - Timeout configuration
        - Response validation
        """
        # 1. Create new user
        create_response = (self.http("Create User")
            .setRequestMethod(HTTPMethod.POST)
            .setBasePath("/users")
            .setJsonBody({
                "name": "John Doe",
                "email": "john@example.com",
                "role": "user"
            })
            .setTimeout(10.0)  # 10 second timeout
            .sendRequest())
        
        # Validate creation response
        create_validator = ResponseValidator(create_response)
        if not create_validator.status_is(201).json_contains("id").validate():
            self.logger.error("Failed to create user")
            return
        
        user_id = create_response["id"]
        
        # 2. Upload user avatar
        upload_response = (self.http("Upload Avatar")
            .setRequestMethod(HTTPMethod.POST)
            .setBasePath(f"/users/{user_id}/avatar")
            .addFile("avatar", "path/to/avatar.jpg", "image/jpeg")
            .addHeader("Authorization", f"Bearer {self.access_token}")
            .sendRequest())
        
        # 3. Update user with query parameters
        update_response = (self.http("Update User")
            .setRequestMethod(HTTPMethod.PUT)
            .setBasePath(f"/users/{user_id}")
            .setJsonBody({"name": "John Updated"})
            .addQueryParams({"validate": "true", "notify": "false"})
            .addHeader("Authorization", f"Bearer {self.access_token}")
            .sendRequest())
    
    @task(3)
    def search_and_filter_users(self):
        """
        Example of searching and filtering users.
        Demonstrates:
        - Query parameters
        - Response validation
        - Logging control
        """
        # Search users with pagination and filters
        search_response = (self.http("Search Users")
            .setRequestMethod(HTTPMethod.GET)
            .setBasePath("/users/search")
            .addQueryParams({
                "page": 1,
                "limit": 10,
                "sort": "name",
                "filter": "active"
            })
            .addHeader("Authorization", f"Bearer {self.access_token}")
            .disableResponseLogging()  # Don't log large response data
            .sendRequest())
        
        # Validate search response
        search_validator = ResponseValidator(search_response)
        if not search_validator.status_is(200).json_contains("items").validate():
            self.logger.error("Search failed")
            return
    
    @task(4)
    def batch_operations(self):
        """
        Example of batch operations with retry mechanism.
        Demonstrates:
        - Batch operations
        - Retry mechanism
        - Error handling
        - Response validation
        """
        # Batch create users
        batch_response = (self.http("Batch Create Users")
            .setRequestMethod(HTTPMethod.POST)
            .setBasePath("/users/batch")
            .setJsonBody({
                "users": [
                    {"name": "User1", "email": "user1@example.com"},
                    {"name": "User2", "email": "user2@example.com"}
                ]
            })
            .addHeader("Authorization", f"Bearer {self.access_token}")
            .setRetryConfig(RetryConfig(
                max_attempts=5,
                delay=2.0,
                backoff_factor=1.5
            ))
            .sendRequest())
        
        # Validate batch response
        batch_validator = ResponseValidator(batch_response)
        if not batch_validator.status_is(200).json_contains("success").validate():
            self.logger.error("Batch operation failed")
            return
    
    @task(5)
    def complex_validation(self):
        """
        Example of complex response validation.
        Demonstrates:
        - Complex JSON validation
        - Header validation
        - Multiple validation checks
        """
        response = (self.http("Get User Details")
            .setRequestMethod(HTTPMethod.GET)
            .setBasePath("/users/details")
            .addHeader("Authorization", f"Bearer {self.access_token}")
            .sendRequest())
        
        # Complex validation
        validator = ResponseValidator(response)
        validator.status_is(200)\
            .has_header("Content-Type")\
            .json_matches({
                "status": "active",
                "role": "user"
            })\
            .json_contains("permissions")
        
        if not validator.validate():
            self.logger.error("Complex validation failed")
            return 