from ..locust_tasks.base import BaseLocustUser
from locust import task, between
from loguru import logger

class SampleUser(BaseLocustUser):
    """Sample user behavior for testing"""
    
    wait_time = between(1, 5)
    
    @task(3)
    def get_homepage(self):
        """Get homepage (weight: 3)"""
        self.make_request("GET", "/", name="Get Homepage")
    
    @task(2)
    def get_about(self):
        """Get about page (weight: 2)"""
        self.make_request("GET", "/about", name="Get About Page")
    
    @task(1)
    def post_contact(self):
        """Submit contact form (weight: 1)"""
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "message": "This is a test message"
        }
        self.make_request(
            "POST",
            "/contact",
            json_data=data,
            expected_status=201,
            name="Submit Contact Form"
        ) 