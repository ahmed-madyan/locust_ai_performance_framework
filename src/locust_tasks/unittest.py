from ..locust_tasks.base import BaseLocustUser, HTTPMethod
from locust import task, between
from loguru import logger


class SampleUser(BaseLocustUser):
    """Sample user behavior for testing"""

    wait_time = between(1, 5)

    baseuri = "https://reqres.in/"

    @task(1)
    def getListOfUser(self):
        response = (self.http("Get List of User")
                    .setBaseUri(self.base_uri)
                    .setRequestMethod(HTTPMethod.GET)
                    .setBasePath("/api/users")
                    .addHeader("page", "2")
                    .sendRequest())

        # Validate response
        if not response.status_code == 200:
            logger.error("Failed to get list of user")
        return
